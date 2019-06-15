# coding: utf-8
import os
import re
import time

from tests.demo_log import FRONT, END
from tests.utils import cst


# {
# "status": "ok",
# "datas": {},
# "settings_py": "logparser/logparser/settings.py",
# "settings": {...},
# "last_update_timestamp": "1546272001"
# "last_update_time": "2019-01-01 00:00:01"
# "logparser_version": "0.8.1",
# }
def test_empty_logs_dir(psr):
    parser = psr(execute_main=False)
    # cst.STATS_JSON_PATH is created in Parser.__init__()
    for path in [cst.LOG_PATH, cst.TXT_PATH, cst.STATS_JSON_PATH]:
        os.remove(path)
    parser.main()
    for path in [cst.LOG_PATH, cst.TXT_PATH, cst.LOG_JSON_PATH, cst.TXT_JSON_PATH]:
        assert not os.path.exists(path)
    assert os.path.exists(cst.STATS_JSON_PATH)
    stats = cst.read_data(cst.STATS_JSON_PATH)
    default_stats = dict(status='ok', datas={}, logparser_version=cst.LOGPARSER_VERSION)
    assert set(stats.keys()) == {'status', 'datas', 'settings_py', 'settings',
                                 'last_update_timestamp', 'last_update_time', 'logparser_version'}
    for k, v in default_stats.items():
        assert stats[k] == v
    # last_update_time, comes from last_update_timestamp
    assert cst.string_to_timestamp(stats['last_update_time']) == stats['last_update_timestamp']


def test_demo_log_files(psr):
    psr()
    log_data = cst.read_data(cst.LOG_JSON_PATH)
    txt_data = cst.read_data(cst.TXT_JSON_PATH)
    for k in cst.PARSE_KEYS:
        if k not in ['last_update_time', 'last_update_timestamp']:
            assert log_data[k] == txt_data[k]

    # 2019-01-01T00_00_01.log
    # 2019-01-01T00_00_02.txt
    for case, data in zip(['log', 'txt'], [log_data, txt_data]):
        cst.check_demo_data(data)

        if case == 'log':
            job = cst.JOB
            ext = 'log'
        else:
            job = cst.JOB_TXT
            ext = 'txt'
        assert data['log_path'].endswith('%s.%s' % (job, ext))
        assert data['json_path'].endswith('%s.json' % job)
        assert data['json_url'].endswith('%s.json' % job)
        assert data['json_url'].startswith('http://%s' % cst.SCRAPYD_SERVER)

        assert data['size'] == cst.SIZE
        assert data['position'] == cst.SIZE
        assert data['status'] == cst.STATUS
        assert data['_head'] == cst.LOG_HEAD_LINES
        assert data['logparser_version'] == cst.LOGPARSER_VERSION


def test_log_no_change(psr):
    start_time = time.time()
    psr(parse_round_interval=1, exit_timeout=0.001)  # parse for first time, exit
    parse_time = time.time() - start_time
    exit_timeout = parse_time * 3  # Ensure a sleep
    interval = exit_timeout + 5
    psr(parse_round_interval=interval, exit_timeout=exit_timeout)
    stats = cst.read_data(cst.STATS_JSON_PATH)
    data = cst.read_data(cst.LOG_JSON_PATH)
    assert stats['datas'][cst.PROJECT][cst.SPIDER][cst.JOB]['last_update_time'] == data['last_update_time']
    # last_update_timestamp does not contain the float part of a timestamp, so add '- 2' on the right
    assert stats['last_update_timestamp'] - data['last_update_timestamp'] > interval - 2


def test_new_file_read_data(psr):
    psr()
    log_data = cst.read_data(cst.LOG_JSON_PATH)
    last_update_timestamp = log_data['last_update_timestamp']

    # Skip parsing since data with same size found
    # Old file with old size
    parser = psr(execute_main=False, reset_logs=False)
    for i in range(2):
        time.sleep(2)
        parser.main()
        log_data = cst.read_data(cst.LOG_JSON_PATH)
        assert log_data['last_update_timestamp'] == last_update_timestamp
        cst.check_demo_data(log_data)

    # Old logfile with smaller size
    cst.write_text(cst.LOG_PATH, FRONT + END.replace('memory', ''))
    parser.main()
    log_data = cst.read_data(cst.LOG_JSON_PATH)
    assert log_data['last_update_timestamp'] == last_update_timestamp
    cst.check_demo_data(log_data)
    stats = cst.read_data(cst.STATS_JSON_PATH)
    assert cst.PROJECT not in stats['datas']
    # -> parse in next round
    parser.main()
    log_data = cst.read_data(cst.LOG_JSON_PATH)
    assert log_data['last_update_timestamp'] > last_update_timestamp
    cst.check_demo_data(log_data)
    stats = cst.read_data(cst.STATS_JSON_PATH)
    assert cst.PROJECT in stats['datas']

    # Read data fail
    time.sleep(2)
    cst.write_text(cst.LOG_JSON_PATH, u'')
    psr(reset_logs=False)
    log_data = cst.read_data(cst.LOG_JSON_PATH)
    assert log_data['last_update_timestamp'] > last_update_timestamp
    cst.check_demo_data(log_data)


def test_new_size_read_data(psr):
    appended_log = u'test'
    appended_log_length = len(appended_log)
    parser = psr()
    log_data = cst.read_data(cst.LOG_JSON_PATH)
    assert log_data['logparser_version'] == cst.LOGPARSER_VERSION
    cst.check_demo_data(log_data)
    last_update_timestamp = log_data['last_update_timestamp']

    # Valid but short appended log
    cst.write_text(cst.LOG_PATH, appended_log, append=True)
    time.sleep(2)
    parser.main()
    assert os.path.getsize(cst.APPENDED_LOG_PATH) == 0
    log_data = cst.read_data(cst.LOG_JSON_PATH)
    assert log_data['last_update_timestamp'] > last_update_timestamp
    assert log_data['size'] == cst.SIZE + appended_log_length
    assert log_data['position'] == cst.SIZE
    cst.check_demo_data(log_data)  # Previous parsed result is not affected by short appended log

    # Mismatching version
    log_data['logparser_version'] = '0.0.0'
    cst.write_text(cst.LOG_JSON_PATH, cst.json_dumps(log_data))
    log_data = cst.read_data(cst.LOG_JSON_PATH)
    assert log_data['logparser_version'] == '0.0.0'

    cst.write_text(cst.LOG_PATH, appended_log, append=True)
    now_size = cst.SIZE + appended_log_length * 2
    parser.main()
    assert os.path.getsize(cst.APPENDED_LOG_PATH) == now_size
    log_data = cst.read_data(cst.LOG_JSON_PATH)
    assert log_data['logparser_version'] == cst.LOGPARSER_VERSION
    assert log_data['size'] == now_size
    assert log_data['position'] == now_size
    cst.check_demo_data(log_data)

    # Broken json file
    cst.write_text(cst.LOG_JSON_PATH, appended_log, append=True)
    cst.write_text(cst.LOG_PATH, appended_log, append=True)
    now_size = cst.SIZE + appended_log_length * 3
    parser.main()
    assert os.path.getsize(cst.APPENDED_LOG_PATH) == now_size
    log_data = cst.read_data(cst.LOG_JSON_PATH)
    assert log_data['size'] == now_size
    assert log_data['position'] == now_size
    cst.check_demo_data(log_data)


def test_actual_lines(psr):
    """
    2019-01-01 00:00:01 DEBUG 1
    a

    b

    2019-01-01 00:00:01 DEBUG 2
    """
    prefix = u'2019-01-01 00:00:01 DEBUG '
    parser = psr(execute_main=False, log_head_lines=5, log_tail_lines=10)
    # In windows, '\r\n' is stored as: '\r\r\n'
    cst.write_text(cst.LOG_PATH, prefix + '1\na\n\nb\n\n')
    cst.write_text(cst.LOG_PATH, prefix + '2\n', append=True)
    parser.main()
    log_data = cst.read_data(cst.LOG_JSON_PATH)
    assert '1\na\n\nb\n\n' in log_data['head']
    assert log_data['_head'] == log_data['head']

    for i in range(3, 8):
        cst.write_text(cst.LOG_PATH, prefix + '%s\n' % i, append=True)
    parser.main()
    log_data = cst.read_data(cst.LOG_JSON_PATH)
    assert log_data['_head'] == 5
    for i in range(1, 8):
        if i <= 3:
            assert 'DEBUG %s' % i in log_data['head']
        else:
            assert 'DEBUG %s' % i not in log_data['head']
    head = log_data['head']

    for i in range(8, 12):
        cst.write_text(cst.LOG_PATH, prefix + '%s\n' % i, append=True)
    parser.main()
    log_data = cst.read_data(cst.LOG_JSON_PATH)
    assert log_data['_head'] == 5
    assert log_data['head'] == head
    assert log_data['tail'].startswith('b\n\n')
    for i in range(2, 11):
        assert 'DEBUG %s' % i in log_data['tail']


def test_appended_log(psr):
    first_log_time = '2018-10-23 18:28:34'

    parser = psr(execute_main=False, log_head_lines=10, log_tail_lines=50)
    # 2018-10-23 18:28:35 [test] WARNING: warn
    front_head, front_tail = re.split(r'WARNING: warn[^i]', FRONT)
    # {'item': 2}
    # 2018-10-23 18:28:40 [..logstats] INFO: Crawled 3 pages (at 60 pages/min), scraped 2 items (at 60 items/min)
    front_mid, front_tail = front_tail.split("{'item': 2}")

    cst.write_text(cst.LOG_PATH, u'')
    # Test short appended log
    for idx, appended_log in enumerate([u'', u'2018-10-23 18:28:34 DEBUG\n',
                                        u'2018-10-23 18:28:34 INFO\n', u'test\n']):
        cst.write_text(cst.LOG_PATH, appended_log, append=True)
        parser.main()
        data = cst.read_data(cst.LOG_JSON_PATH)
        # Text to be ignored for next round: '2018-10-23 18:28:34 INFO\r\n'
        # appended log: 2018-10-23 18:28:34 DEBUG
        # "_head": "2018-10-23 18:28:34 DEBUG\n",
        # "head": "2018-10-23 18:28:34 DEBUG\n",
        # "tail": "2018-10-23 18:28:34 DEBUG\n",
        if idx >= 2:
            assert data['first_log_time'] == first_log_time
            assert data['_head']
        else:
            assert data['first_log_time'] == cst.NA
            assert not data['_head']
        assert data['finish_reason'] == cst.NA
        assert data['pages'] is None
        assert data['items'] is None

    cst.write_text(cst.LOG_PATH, front_head, append=True)
    parser.main()
    data = cst.read_data(cst.LOG_JSON_PATH)
    assert data['first_log_time'] == first_log_time
    assert data['latest_log_time'] == '2018-10-23 18:28:35'
    assert data['datas'] == [['2018-10-23 18:28:35', 0, 0, 0, 0]]
    assert data['pages'] == 0
    assert data['items'] == 0
    for k in cst.LATEST_MATCHES_RESULT_DICT.keys():
        if k in ['scrapy_version', 'telnet_console', 'resuming_crawl', 'latest_stat']:
            assert data['latest_matches'][k]
        else:
            assert not data['latest_matches'][k]
    for k in cst.LOG_CATEGORIES_RESULT_DICT.keys():
        assert data['log_categories'][k]['count'] == 0
        assert data['log_categories'][k]['details'] == []
    assert data['shutdown_reason'] == cst.NA
    assert data['finish_reason'] == cst.NA
    assert '[scrapy.utils.log] INFO: Scrapy 1.5.1 started' in data['head']
    assert '[scrapy.utils.log] INFO: Scrapy 1.5.1 started' in data['tail']

    cst.write_text(cst.LOG_PATH, u'WARNING: warn\n' + front_mid, append=True)
    parser.main()
    data = cst.read_data(cst.LOG_JSON_PATH)
    assert data['first_log_time'] == first_log_time
    assert data['latest_log_time'] == '2018-10-23 18:28:39'
    assert (data['datas'][0] == ['2018-10-23 18:28:35', 0, 0, 0, 0]
            and ['2018-10-23 18:28:37', 1, 60, 0, 0] in data['datas']
            and ['2018-10-23 18:28:38', 2, 60, 1, 60] in data['datas']
            and data['datas'][-1] == ['2018-10-23 18:28:39', 2, 0, 1, 0]
            and len(data['datas']) == 5)
    assert data['pages'] == 2
    assert data['items'] == 1
    for k in cst.LATEST_MATCHES_RESULT_DICT.keys():
        if k in ['telnet_username', 'telnet_password']:
            assert not data['latest_matches'][k]
        else:
            assert data['latest_matches'][k]
    assert data['latest_matches']['latest_item'] == "{'item': 1}"
    for k, (count, __) in cst.LOG_CATEGORIES_RESULT_DICT.items():
        if k == 'error_logs':
            assert data['log_categories'][k]['count'] == 4
        elif k == 'retry_logs':
            assert data['log_categories'][k]['count'] == 0
        else:
            assert data['log_categories'][k]['count'] == count
        if k == 'retry_logs':
            assert data['log_categories'][k]['details'] == []
        else:
            assert data['log_categories'][k]['details']
    assert data['shutdown_reason'] == cst.NA
    assert data['finish_reason'] == cst.NA

    cst.write_text(cst.LOG_PATH, u"{'item': 2}" + front_tail, append=True)
    parser.main()
    data = cst.read_data(cst.LOG_JSON_PATH)
    assert data['first_log_time'] == first_log_time
    assert data['latest_log_time'] == '2018-10-23 18:29:41'
    assert (data['datas'][0] == ['2018-10-23 18:28:35', 0, 0, 0, 0]
            and data['datas'][-1] == ['2018-10-23 18:29:41', 3, 0, 2, 0]
            and len(data['datas']) == 67)
    assert data['pages'] == 3
    assert data['items'] == 2
    for k in cst.LATEST_MATCHES_RESULT_DICT.keys():
        if k in ['telnet_username', 'telnet_password']:
            assert not data['latest_matches'][k]
        else:
            assert data['latest_matches'][k]
    for k, (count, __) in cst.LOG_CATEGORIES_RESULT_DICT.items():
        assert data['log_categories'][k]['count'] == count
        assert data['log_categories'][k]['details']
    assert data['shutdown_reason'] == cst.NA
    assert data['finish_reason'] == cst.NA

    # 'finish_reason': 'finished',
    # 'finish_time': datetime.datetime(2018, 10, 23, 10, 29, 41, 174719),
    end_head, end_tail = END.split("'finish_time'")
    cst.write_text(cst.LOG_PATH, end_head, append=True)
    parser.main()
    data = cst.read_data(cst.LOG_JSON_PATH)
    assert data['first_log_time'] == first_log_time
    assert data['latest_log_time'] == '2018-10-23 18:29:41'
    assert (data['datas'][0] == ['2018-10-23 18:28:35', 0, 0, 0, 0]
            and data['datas'][-1] == ['2018-10-23 18:29:41', 3, 0, 2, 0]
            and len(data['datas']) == 67)
    assert data['pages'] == 3
    assert data['items'] == 2
    for k in cst.LATEST_MATCHES_RESULT_DICT.keys():
        if k in ['telnet_username', 'telnet_password']:
            assert not data['latest_matches'][k]
        else:
            assert data['latest_matches'][k]
    for k, (count, __) in cst.LOG_CATEGORIES_RESULT_DICT.items():
        assert data['log_categories'][k]['count'] == count
        assert data['log_categories'][k]['details']
    assert data['shutdown_reason'] == cst.NA
    assert data['finish_reason'] == cst.NA
    # 2018-10-23 18:29:41 [scrapy.extensions.feedexport] INFO: Stored jsonlines feed (2 items) in: file:///
    # 2018-10-23 18:29:41 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
    assert 'INFO: Stored jsonlines feed' in data['tail']
    assert 'INFO: Dumping Scrapy stats:' not in data['tail']

    cst.write_text(cst.LOG_PATH, u"'finish_time'" + end_tail, append=True)
    parser.main()
    data = cst.read_data(cst.LOG_JSON_PATH)
    assert data['first_log_time'] == first_log_time
    assert data['latest_log_time'] == '2018-10-23 18:29:42'
    assert (data['datas'][0] == ['2018-10-23 18:28:35', 0, 0, 0, 0]
            and data['datas'][-1] == ['2018-10-23 18:29:41', 3, 0, 2, 0]
            and len(data['datas']) == 67)
    assert data['pages'] == 3
    assert data['items'] == 2
    for k in cst.LATEST_MATCHES_RESULT_DICT.keys():
        if k in ['telnet_username', 'telnet_password']:
            assert not data['latest_matches'][k]
        else:
            assert data['latest_matches'][k]
    for k, (count, __) in cst.LOG_CATEGORIES_RESULT_DICT.items():
        assert data['log_categories'][k]['count'] == count
        assert data['log_categories'][k]['details']
    assert data['shutdown_reason'] == cst.NA
    assert data['finish_reason'] == 'finished'
    # assert data['size'] == 15883  # != cst.SIZE 15862 '2018-10-23 18:28:34\n' \r\n => 15883
    # assert data['position'] == 15883  # != cst.SIZE 15862
    assert data['size'] == data['position']
    assert '[scrapy.utils.log] INFO: Scrapy 1.5.1 started' in data['head']
    assert '[scrapy.core.engine] INFO: Spider closed' not in data['head']
    assert '[scrapy.utils.log] INFO: Scrapy 1.5.1 started' not in data['tail']
    assert '[scrapy.core.engine] INFO: Spider closed' in data['tail']
