# coding: utf-8
import io
import os
from shutil import copy
import time

from tests.demo_log import END
from tests.utils import cst


# SCRAPYD_SERVER = '127.0.0.1:6800'
def test_scrapyd_server(psr):
    default = '127.0.0.1:6800'
    json_url = 'http://%s/logs/%s/%s/%s.json' % (default, cst.PROJECT, cst.SPIDER, cst.JOB)
    psr()
    stats = cst.read_data(cst.STATS_JSON_PATH)
    assert stats['datas'][cst.PROJECT][cst.SPIDER][cst.JOB]['json_url'] == json_url

    localhost = 'localhost:6800'
    json_url = 'http://%s/logs/%s/%s/%s.json' % (localhost, cst.PROJECT, cst.SPIDER, cst.JOB)
    psr(scrapyd_server=localhost)
    stats = cst.read_data(cst.STATS_JSON_PATH)
    assert stats['datas'][cst.PROJECT][cst.SPIDER][cst.JOB]['json_url'] == json_url


# SCRAPYD_LOGS_DIR = ''
def test_scrapyd_logs_dir(psr):
    paths_fixed = [cst.LOGS_PATH, cst.LOG_PATH, cst.TXT_PATH, cst.GBK_LOG_PATH, cst.STATS_JSON_PATH]
    paths_generated = [cst.LOG_JSON_PATH, cst.TXT_JSON_PATH, cst.APPENDED_LOG_PATH,
                       cst.DATAS_COMPLETE_JSON_PATH, cst.DATAS_SIMPLIFIED_JSON_PATH]
    paths_not_exist = [os.path.join(cst.LOGS_PATH, 'gbk.json'),
                       os.path.join(cst.LOGS_PATH, cst.PROJECT, cst.SPIDER, 'gbk.json'),
                       os.path.join(cst.LOGS_PATH, cst.PROJECT_TXT, cst.SPIDER_TXT, 'gbk.json')]

    parser = psr(execute_main=False)
    for path in paths_fixed:
        assert os.path.exists(path)
    for path in paths_generated + paths_not_exist:
        assert not os.path.exists(path)
    parser.main()
    for path in paths_fixed + paths_generated:
        assert os.path.exists(path)
    for path in paths_not_exist:
        assert not os.path.exists(path)


# PARSE_ROUND_INTERVAL = 10
def test_parse_round_interval(psr):
    # mtime = os.path.getmtime(cst.LOG_JSON_PATH)
    start_time = time.time()
    psr(parse_round_interval=1, exit_timeout=0.001)  # parse for first time, exit
    parse_time = time.time() - start_time
    exit_timeout = parse_time * 3  # Ensure a sleep
    for interval in [exit_timeout + 5, (exit_timeout + 5) * 3]:
        start_time = time.time()
        # parse for first time, sleep interval, parse for second time, exit
        psr(parse_round_interval=interval, exit_timeout=exit_timeout)
        assert time.time() - start_time > interval


# ENABLE_TELNET = True
def test_disable_telnet(psr):
    parser = psr(execute_main=False, enable_telnet=True)
    assert parser.ENABLE_TELNET

    parser = psr(execute_main=False, enable_telnet=False)
    assert not parser.ENABLE_TELNET


# LOG_ENCODING = 'utf-8'
def test_log_encoding(psr):
    # TCP connection timed out: 10060: 由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败。.
    psr()
    data = cst.read_data(cst.LOG_JSON_PATH)
    for detail in data['log_categories']['retry_logs']['details']:
        assert u'连接尝试失败' in detail

    psr(log_encoding='gbk')
    data = cst.read_data(cst.LOG_JSON_PATH)
    for detail in data['log_categories']['retry_logs']['details']:
        assert u'连接尝试失败' not in detail and 'TCP connection timed out: 10060:' in detail

    # 2018-10-23 18:28:33 [test] 3: test utf8: 测试中文
    parser = psr(execute_main=False, log_encoding=cst.LOG_ENCODING)
    copy(cst.GBK_LOG_PATH, cst.LOG_PATH)
    parser.main()
    data = cst.read_data(cst.LOG_JSON_PATH)
    assert '2018-10-23 18:28:33 [test] 3: test utf8:' in data['head'] and u'测试中文' not in data['head']

    parser = psr(execute_main=False, log_encoding='gbk')
    copy(cst.GBK_LOG_PATH, cst.LOG_PATH)
    parser.main()
    data = cst.read_data(cst.LOG_JSON_PATH)
    assert '2018-10-23 18:28:33 [test] 3: test utf8:' in data['head'] and u'测试中文' in data['head']


# LOG_EXTENSIONS=['.log', '.txt']
def test_log_extensions(psr):
    if os.path.exists(cst.STATS_JSON_PATH):
        os.remove(cst.STATS_JSON_PATH)
    psr(log_extensions=[])
    stats = cst.read_data(cst.STATS_JSON_PATH)
    assert stats['datas'] == {}

    psr(log_extensions=['.log'])
    stats = cst.read_data(cst.STATS_JSON_PATH)
    assert len(stats['datas']) == 1 and cst.JOB in stats['datas'][cst.PROJECT][cst.SPIDER]

    psr(log_extensions=['.txt'])
    stats = cst.read_data(cst.STATS_JSON_PATH)
    assert len(stats['datas']) == 1 and cst.JOB_TXT in stats['datas'][cst.PROJECT_TXT][cst.SPIDER_TXT]

    psr(log_extensions=cst.LOG_EXTENSIONS)
    stats = cst.read_data(cst.STATS_JSON_PATH)
    assert (len(stats['datas']) == 2
            and cst.JOB in stats['datas'][cst.PROJECT][cst.SPIDER]
            and cst.JOB_TXT in stats['datas'][cst.PROJECT_TXT][cst.SPIDER_TXT])


# LOG_HEAD_LINES = 100, LOG_TAIL_LINES = 200
def test_log_headlines_taillines(psr):
    psr(log_head_lines=5, log_tail_lines=10)
    data = cst.read_data(cst.LOG_JSON_PATH)
    assert len(data['head'].split('\n')) == 5
    assert len(data['tail'].split('\n')) == 10


# LOG_CATEGORIES_LIMIT = 10
def test_log_categories_limit(psr):
    log_categories_limit = 3
    parser = psr(log_categories_limit=log_categories_limit)
    data = cst.read_data(cst.LOG_JSON_PATH)
    cst.check_demo_data(data, log_categories_limit=log_categories_limit)


# JOBS_TO_KEEP=100
def test_jobs_to_keep(psr):
    parser = psr()
    datas_full = cst.read_data(cst.DATAS_COMPLETE_JSON_PATH)
    datas_simplified = cst.read_data(cst.DATAS_SIMPLIFIED_JSON_PATH)
    for datas in [datas_full, datas_simplified]:
        assert set(datas.keys()) == {cst.LOG_PATH, cst.TXT_PATH}
    # delete a logfile
    os.remove(cst.TXT_PATH)
    parser.main()
    datas_full = cst.read_data(cst.DATAS_COMPLETE_JSON_PATH)
    datas_simplified = cst.read_data(cst.DATAS_SIMPLIFIED_JSON_PATH)
    for datas in [datas_full, datas_simplified]:
        assert set(datas.keys()) == {cst.LOG_PATH, cst.TXT_PATH}
    # add a logfile
    copy(cst.LOG_PATH, cst.LOG_TEMP_PATH)
    parser.main()
    datas_full = cst.read_data(cst.DATAS_COMPLETE_JSON_PATH)
    datas_simplified = cst.read_data(cst.DATAS_SIMPLIFIED_JSON_PATH)
    for datas in [datas_full, datas_simplified]:
        assert set(datas.keys()) == {cst.LOG_PATH, cst.TXT_PATH, cst.LOG_TEMP_PATH}

    parser = psr(jobs_to_keep=1)
    datas_full = cst.read_data(cst.DATAS_COMPLETE_JSON_PATH)
    datas_simplified = cst.read_data(cst.DATAS_SIMPLIFIED_JSON_PATH)
    for datas in [datas_full, datas_simplified]:
        assert set(datas.keys()) == {cst.LOG_PATH, cst.TXT_PATH}
    # delete a logfile
    os.remove(cst.TXT_PATH)
    parser.main()
    datas_full = cst.read_data(cst.DATAS_COMPLETE_JSON_PATH)
    assert set(datas_full.keys()) == {cst.LOG_PATH, cst.TXT_PATH}
    datas_simplified = cst.read_data(cst.DATAS_SIMPLIFIED_JSON_PATH)
    assert set(datas_simplified.keys()) == {cst.LOG_PATH}
    # add a logfile
    copy(cst.LOG_PATH, cst.LOG_TEMP_PATH)
    parser.main()
    datas_full = cst.read_data(cst.DATAS_COMPLETE_JSON_PATH)
    datas_simplified = cst.read_data(cst.DATAS_SIMPLIFIED_JSON_PATH)
    for datas in [datas_full, datas_simplified]:
        assert set(datas.keys()) == {cst.LOG_PATH, cst.LOG_TEMP_PATH}


# CHUNK_SIZE = 10 * 1000 * 1000  # 10 MB
def test_chunk_size(psr):
    parser = psr(execute_main=False)
    os.remove(cst.TXT_PATH)
    assert not os.path.isdir(cst.TXT_PATH)
    parser.main()
    data = cst.read_data(cst.LOG_JSON_PATH)
    assert data['first_log_time'] == '2018-10-23 18:28:34'
    assert data['latest_log_time'] == '2018-10-23 18:29:42'
    cst.check_demo_data(data)
    assert os.path.getsize(cst.APPENDED_LOG_PATH) == cst.SIZE

    parser = psr(execute_main=False, chunk_size=10000)  # 15,862 = 9924 + 5938, 15683 = 9938 + 5745
    os.remove(cst.TXT_PATH)
    assert not os.path.isdir(cst.TXT_PATH)
    parser.main()
    data = cst.read_data(cst.LOG_JSON_PATH)
    cst.json_dumps(data)
    assert data['first_log_time'] == '2018-10-23 18:28:34'
    assert data['latest_log_time'] == '2018-10-23 18:29:42'
    cst.check_demo_data(data)
    assert os.path.getsize(cst.APPENDED_LOG_PATH) == 5938 if len(os.linesep) == 2 else 5745


# DELETE_EXISTING_JSON_FILES_AT_STARTUP = False
# Executed in Parser.__init__()
def test_delete_json_files(psr):
    psr()
    for path in [cst.LOG_JSON_PATH, cst.TXT_JSON_PATH]:
        assert os.path.exists(path)
    with io.open(cst.LOG_JSON_TEMP_PATH, 'w', encoding=cst.LOG_ENCODING) as f:
        f.write(u'')

    parser = psr(execute_main=False, reset_logs=False, delete_existing_json_files_at_startup=False)
    for path in [cst.LOG_JSON_PATH, cst.TXT_JSON_PATH, cst.LOG_JSON_TEMP_PATH]:
        assert os.path.exists(path)
    parser.main()
    for path in [cst.LOG_JSON_PATH, cst.TXT_JSON_PATH, cst.LOG_JSON_TEMP_PATH]:
        assert os.path.exists(path)

    parser = psr(execute_main=False, reset_logs=False, delete_existing_json_files_at_startup=True)
    for path in [cst.LOG_JSON_PATH, cst.TXT_JSON_PATH, cst.LOG_JSON_TEMP_PATH]:
        assert not os.path.exists(path)
    parser.main()
    for path in [cst.LOG_JSON_PATH, cst.TXT_JSON_PATH]:
        assert os.path.exists(path)
    assert not os.path.exists(cst.LOG_JSON_TEMP_PATH)


# KEEP_DATA_IN_MEMORY = False
def test_keep_data_in_memory(psr):
    datas_full_keys_set = set(cst.META_KEYS + cst.PARSE_KEYS + cst.FULL_EXTENDED_KEYS)
    datas_simplified_keys_set = set(cst.META_KEYS + cst.SIMPLIFIED_KEYS)

    parser = psr(keep_data_in_memory=True)
    datas_full = cst.read_data(cst.DATAS_COMPLETE_JSON_PATH)
    for k in [cst.LOG_PATH, cst.TXT_PATH]:
        assert set(datas_full[k].keys()) == datas_full_keys_set
    datas_simplified = cst.read_data(cst.DATAS_SIMPLIFIED_JSON_PATH)
    for k in [cst.LOG_PATH, cst.TXT_PATH]:
        assert set(datas_simplified[k].keys()) == datas_full_keys_set
    # keys_redundant
    # DEBUG: Simplify demo_txt/test_txt/2019-01-01T00_00_02 in memory
    os.remove(cst.TXT_PATH)
    parser.main()
    datas_full = cst.read_data(cst.DATAS_COMPLETE_JSON_PATH)
    for k in [cst.LOG_PATH, cst.TXT_PATH]:
        assert set(datas_full[k].keys()) == datas_full_keys_set
    datas_simplified = cst.read_data(cst.DATAS_SIMPLIFIED_JSON_PATH)
    assert set(datas_simplified[cst.LOG_PATH].keys()) == datas_full_keys_set
    assert set(datas_simplified[cst.TXT_PATH].keys()) == datas_simplified_keys_set

    parser = psr(keep_data_in_memory=False)
    datas_full = cst.read_data(cst.DATAS_COMPLETE_JSON_PATH)
    for k in [cst.LOG_PATH, cst.TXT_PATH]:
        assert set(datas_full[k].keys()) == datas_full_keys_set
    datas_simplified = cst.read_data(cst.DATAS_SIMPLIFIED_JSON_PATH)
    for k in [cst.LOG_PATH, cst.TXT_PATH]:
        assert set(datas_simplified[k].keys()) == datas_simplified_keys_set
    # New round of parsing, old file with new size, test self.cst.read_data(), found invalid cst.LOG_JSON_PATH
    cst.write_text(cst.LOG_PATH, u'appended_log\n', append=True)
    parser.main()
    cst.write_text(cst.LOG_JSON_PATH, u'')
    cst.write_text(cst.LOG_PATH, END, append=True)
    parser.main()


# VERBOSE = False
def test_verbose(psr):
    psr(verbose=True)
    psr(verbose=False)
