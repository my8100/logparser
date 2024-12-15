# coding: utf-8
import os
import platform
import re
import time

# Used in test_telnet_fail()
from tests.demo_log import TELNET_151_NO_PORT, TELNET_151_PORT_16023, TELNET_160_PORT_16024
from tests.utils import cst


# Linux-5.0.9-301.fc30.x86_64-x86_64-with-fedora-30-Thirty'
on_fedora = 'fedora' in platform.platform()


def test_telnet(psr):
    # https://docs.scrapy.org/en/latest/topics/telnetconsole.html
    parser = psr(execute_main=False)

    cwd = os.getcwd()
    print(cwd)
    os.chdir(cst.DEMO_PROJECT_PATH)
    print(os.getcwd())
    # ['1.4.0', '1.5.0', '1.5.1', '1.5.2', '1.6.0', 'latest']
    # Ref: https://github.com/scrapy/scrapy/issues/6024
    # "We just released 2.10.1 with the Twisted version restricted as a workaround for this."
    # Ref: https://github.com/scrapy/scrapy/pull/6064
    # Fixes #6024
    try:
        # scrapyd 1.4.3 requires scrapy>=2.0.0
        cst.sub_process('pip uninstall -y scrapyd', block=True)
        cst.sub_process('pip uninstall -y scrapy', block=True)
        for version in ['latest', '2.10.1', '2.12.0']:
            if version == 'latest':
                pip_cmd = 'pip install --upgrade scrapy'
            else:
                # cst.sub_process('pip uninstall -y Twisted', block=True)
                if version < '2.10.1':
                    cst.sub_process('pip install Twisted==20.3.0', block=True)
                pip_cmd = 'pip install scrapy==%s' % version
            cst.sub_process(pip_cmd, block=True)
            log_file = os.path.join(cst.DEMO_PROJECT_LOG_FOLDER_PATH, 'scrapy_%s.log' % version)
            scrapy_cmd = 'scrapy crawl example -s CLOSESPIDER_TIMEOUT=20 -s LOG_FILE=%s' % log_file
            if version == '2.10.1':
                scrapy_cmd += ' -s TELNETCONSOLE_ENABLED=False'
            elif version == '2.12.0':
                scrapy_cmd += ' -s TELNETCONSOLE_USERNAME=usr123 -s TELNETCONSOLE_PASSWORD=psw456'
            proc = cst.sub_process(scrapy_cmd)

            time.sleep(10)
            if version == '1.4.0':
                proc.kill()
            parser.main()

            if version != '1.4.0':
                time.sleep(20)
            parser.main()

            log_data = cst.read_data(re.sub(r'.log$', '.json', log_file))
            if version == 'latest':
                assert log_data['latest_matches']['scrapy_version'] >= '1.6.0'
            else:
                assert log_data['latest_matches']['scrapy_version'] == version
            assert log_data['log_categories']['critical_logs']['count'] == 0
            assert log_data['log_categories']['error_logs']['count'] == 0
            if version == '2.10.1':
                assert not log_data['latest_matches']['telnet_console']
            else:
                assert log_data['latest_matches']['telnet_console']
            if version <= '1.5.1':
                assert not log_data['latest_matches']['telnet_username']
                assert not log_data['latest_matches']['telnet_password']
            elif version == '2.12.0':
                assert log_data['latest_matches']['telnet_username'] == 'usr123'
                assert log_data['latest_matches']['telnet_password'] == 'psw456'
            else:
                assert not log_data['latest_matches']['telnet_username']
                assert log_data['latest_matches']['telnet_password']
            if version == '1.4.0':
                assert log_data['finish_reason'] == 'N/A'
                assert not log_data['crawler_stats']
                assert not log_data['crawler_engine']
            else:
                assert log_data['finish_reason'] == 'closespider_timeout'
                assert log_data['crawler_stats']
                assert log_data['crawler_stats']['source'] == 'log'
                if version == '2.10.1' or ((cst.ON_WINDOWS or on_fedora) and version > '1.5.1'):
                    assert not log_data['crawler_engine']
                else:
                    assert log_data['crawler_engine']
                    assert log_data['crawler_engine']['source'] == 'telnet'
    except:
        os.chdir(cwd)
        raise
    finally:
        os.chdir(cwd)


def test_disable_telnet(psr):
    last_update_timestamp = 0
    runtime = 0
    cwd = os.getcwd()
    os.chdir(cst.DEMO_PROJECT_PATH)
    try:
        # if cst.ON_WINDOWS or on_fedora:
        #     version = '1.5.1'
        #     pip_cmd = 'pip install scrapy==%s' % version
        # else:
        version = None
        pip_cmd = 'pip install --upgrade scrapy'
        cst.sub_process(pip_cmd, block=True)
        for name in ['enable_telnet', 'disable_telnet']:
            enable_telnet = name == 'enable_telnet'
            parser = psr(execute_main=False, enable_telnet=enable_telnet)
            # Test MyTelnet.verify_log_file_path()
            if enable_telnet:
                for _name in ['6023', '6024']:
                    _log_file = os.path.join(cst.DEMO_PROJECT_LOG_FOLDER_PATH, '%s.log' % _name)
                    cst.write_text(_log_file, TELNET_151_PORT_16023.replace(':16023', ':%s' % _name))

            log_file = os.path.join(cst.DEMO_PROJECT_LOG_FOLDER_PATH, '%s.log' % name)
            scrapy_cmd = 'scrapy crawl example -s CLOSESPIDER_TIMEOUT=40 -s LOG_FILE=%s' % log_file
            cst.sub_process(scrapy_cmd)
            time.sleep(10)
            parser.main()
            if enable_telnet:
                log_data = cst.read_data(re.sub(r'.log$', '.json', log_file))
                last_update_timestamp = log_data['crawler_stats']['last_update_timestamp']
                assert last_update_timestamp
                runtime = log_data['crawler_engine']['time()-engine.start_time']
                assert runtime
            time.sleep(10)
            parser.main()
            # Issue #4: Stats collected via telnet are not being updated periodically
            if enable_telnet:
                log_data = cst.read_data(re.sub(r'.log$', '.json', log_file))
                assert log_data['crawler_stats']['last_update_timestamp'] > last_update_timestamp
                assert log_data['crawler_engine']['time()-engine.start_time'] > runtime
            time.sleep(30)
            parser.main()
            log_data = cst.read_data(re.sub(r'.log$', '.json', log_file))
            if version:
                assert log_data['latest_matches']['scrapy_version'] == version
            assert log_data['latest_matches']['telnet_console']
            assert log_data['crawler_stats']['source'] == 'log'
            if enable_telnet:
                assert log_data['crawler_engine']
            else:
                assert not log_data['crawler_engine']
    except:
        os.chdir(cwd)
        raise
    finally:
        os.chdir(cwd)


def test_telnet_fail(psr):
    parser = psr(execute_main=False)
    for name in ['telnet_151_port_16023', 'telnet_160_port_16024', 'telnet_151_no_port']:
        log_file = os.path.join(cst.DEMO_PROJECT_LOG_FOLDER_PATH, '%s.log' % name)
        cst.write_text(log_file, globals()[name.upper()])
        parser.main()
        log_data = cst.read_data(re.sub(r'.log$', '.json', log_file))
        if name == 'telnet_151_port_16023':
            assert log_data['latest_matches']['scrapy_version'] == '1.5.1'
            assert log_data['latest_matches']['telnet_console'] == '127.0.0.1:16023'
        elif name == 'telnet_160_port_16024':
            assert log_data['latest_matches']['scrapy_version'] == '1.6.0'
            assert log_data['latest_matches']['telnet_console'] == '127.0.0.1:16024'
        else:
            assert log_data['latest_matches']['scrapy_version'] == '1.5.1'
            assert log_data['latest_matches']['telnet_console'] == 'localhost'
        assert not log_data['crawler_engine']
