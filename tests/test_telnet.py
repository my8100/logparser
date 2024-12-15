# coding: utf-8
import os
import platform
import re
import sys
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
        # scrapy 2.12.0: Dropped support for Python 3.8, added support for Python 3.13
        # history: 2.10.1, 2.11.0, 2.11.1, 2.11.2, 2.12.0
        test_type_to_version = dict(
            latest='latest',
            account='2.11.1',
            no_telnet='2.11.0',
        )
        if cst.PY313:
            # TODO: update version
            test_type_to_version.update(no_telnet='latest', account='latest')
        for test_type, version in test_type_to_version.items():
            if version == 'latest':
                pip_cmd = 'pip install --upgrade scrapy'
            else:
                # cst.sub_process('pip uninstall -y Twisted', block=True)
                if version < '2.10.1':
                    cst.sub_process('pip install Twisted==20.3.0', block=True)
                pip_cmd = 'pip install scrapy==%s' % version

            log_file = os.path.join(cst.DEMO_PROJECT_LOG_FOLDER_PATH, 'scrapy_%s.log' % version)
            scrapy_cmd = 'scrapy crawl example -s CLOSESPIDER_TIMEOUT=20 -s LOG_FILE=%s' % log_file
            if test_type == 'no_telnet':
                scrapy_cmd += ' -s TELNETCONSOLE_ENABLED=False'
            elif test_type == 'account':
                scrapy_cmd += ' -s TELNETCONSOLE_USERNAME=usr123 -s TELNETCONSOLE_PASSWORD=psw456'

            print('test_type:', test_type)
            print('version:', version)
            print('pip_cmd:', pip_cmd)
            print('scrapy_cmd:', scrapy_cmd)
            cst.sub_process(pip_cmd, block=True)
            proc = cst.sub_process(scrapy_cmd)

            time.sleep(10)
            if version == '1.4.0':
                proc.kill()
            parser.main()

            if version != '1.4.0':
                time.sleep(20)
            parser.main()

            log_data = cst.read_data(re.sub(r'.log$', '.json', log_file))
            print('log_data: %s' % log_data)

            if version == 'latest':
                assert log_data['latest_matches']['scrapy_version'] >= '1.6.0'
            else:
                assert log_data['latest_matches']['scrapy_version'] == version

            assert log_data['log_categories']['critical_logs']['count'] == 0
            assert log_data['log_categories']['error_logs']['count'] == 0

            if test_type == 'no_telnet':
                assert not log_data['latest_matches']['telnet_console']
            else:
                assert log_data['latest_matches']['telnet_console']

            if test_type == 'no_telnet':
                assert not log_data['latest_matches']['telnet_username']
                assert not log_data['latest_matches']['telnet_password']
            elif test_type == 'account':
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
                if test_type == 'no_telnet' or ((cst.ON_WINDOWS or on_fedora) and version > '1.5.1'):
                    assert not log_data['crawler_engine']
                else:
                    assert log_data['crawler_engine']
                    assert log_data['crawler_engine']['source'] == 'telnet'
    except Exception as err:
        if cst.PY2:
            print("Found error in test: %s" % err)
        else:
            raise err
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
        cst.sub_process('pip uninstall -y Twisted', block=True)
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
                print('log_data: %s' % log_data)
                last_update_timestamp = log_data['crawler_stats']['last_update_timestamp']
                assert last_update_timestamp
                runtime = log_data['crawler_engine']['time()-engine.start_time']
                print(time.ctime(), 'runtime: %s' % runtime)
                assert runtime
            time.sleep(10)
            parser.main()
            # Issue #4: Stats collected via telnet are not being updated periodically
            if enable_telnet:
                log_data = cst.read_data(re.sub(r'.log$', '.json', log_file))
                print('log_data: %s' % log_data)
                assert log_data['crawler_stats']['last_update_timestamp'] > last_update_timestamp
                runtime_new = log_data['crawler_engine']['time()-engine.start_time']
                print(time.ctime(), 'runtime_new: %s' % runtime_new)
                assert runtime_new > runtime
            time.sleep(30)
            parser.main()
            log_data = cst.read_data(re.sub(r'.log$', '.json', log_file))
            print('log_data: %s' % log_data)
            if version:
                assert log_data['latest_matches']['scrapy_version'] == version
            assert log_data['latest_matches']['telnet_console']
            assert log_data['crawler_stats']['source'] == 'log'
            if enable_telnet:
                assert log_data['crawler_engine']
            else:
                assert not log_data['crawler_engine']
    except Exception as err:
        if cst.PY2:
            print("Found error in test: %s" % err)
        else:
            raise err
    finally:
        os.chdir(cwd)


def test_telnet_fail(psr):
    parser = psr(execute_main=False)
    for name in ['telnet_151_port_16023', 'telnet_160_port_16024', 'telnet_151_no_port']:
        log_file = os.path.join(cst.DEMO_PROJECT_LOG_FOLDER_PATH, '%s.log' % name)
        cst.write_text(log_file, globals()[name.upper()])
        parser.main()
        log_data = cst.read_data(re.sub(r'.log$', '.json', log_file))
        print('log_data: %s' % log_data)
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
