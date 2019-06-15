# coding: utf-8
from logparser import parse

from tests.demo_log import (ERROR_404, SHUTDOWN, FRONT, END, TELNET_160_DEFAULT, TELNET_160_USERNAME,
                            TELNET_160_PASSWORD, TELNET_160_USERNAME_PASSWORD)
from tests.utils import cst


# empty log
def test_invalid_log():
    for text in ["", ERROR_404]:
        data = parse(text)
        cst.json_dumps(data)
        if not text:
            assert not (data['head'] or data['tail'])
        else:
            assert '404 - No Such Resource' in data['head'] and '404 - No Such Resource' in data['tail']

        assert set(data.keys()) == set(cst.PARSE_KEYS)
        for k in ['first_log_time', 'latest_log_time', 'runtime', 'shutdown_reason', 'finish_reason']:
            assert data[k] == cst.NA
        for k in ['first_log_timestamp', 'latest_log_timestamp', 'latest_crawl_timestamp', 'latest_scrape_timestamp']:
            assert data[k] == 0
        for k in ['pages', 'items']:
            assert data[k] is None
        # assert data['last_update_timestamp'] > 0  # 1546272001
        # assert len(data['last_update_time']) == 19  # "2019-01-01 00:00:01"
        assert cst.string_to_timestamp(data['last_update_time']) == data['last_update_timestamp']
        assert data['datas'] == []

        for v in data['latest_matches'].values():
            assert v == ''
        assert set(data['latest_matches'].keys()) == set(cst.LATEST_MATCHES_RESULT_DICT.keys())

        for v in data['log_categories'].values():
            assert v == dict(count=0, details=[])
        assert set(data['log_categories'].keys()) == set(cst.LOG_CATEGORIES_RESULT_DICT.keys())


def test_demo_log():
    modified_logstats = FRONT.replace("Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)",
                                      "Crawled 1 pages (at 2 pages/min), scraped 3 items (at 4 items/min)")
    for case, text in zip(['without_stats_dumped', 'whole_log', 'modified_logstats'],
                          [FRONT, FRONT + END, modified_logstats + END]):
        data = parse(text, headlines=50, taillines=100)  # 180 lines in total
        # cst.json_dumps(data)

        if case == 'without_stats_dumped':
            cst.check_demo_data(data, without_stats_dumped=True)
        elif case == 'modified_logstats':  # to test update_data_with_crawler_stats()
            cst.check_demo_data(data, without_stats_dumped=False, modified_logstats=True)
        else:
            cst.check_demo_data(data, without_stats_dumped=False)


def test_latest_item_unicode_escape():
    text = (FRONT + END).replace("{'item': 2}", u"{u'Chinese \\u6c49\\u5b57': 2}")
    data = parse(text)
    assert data['latest_matches']['latest_item'] == u"{u'Chinese 汉字': 2}"


def test_only_stats_dumped():
    replaces = [
        ("'downloader/response_status_count/302': 1,",
         "'downloader/response_status_count/302': 7,\n 'downloader/response_status_count/301': 8,"),
        ("'response_received_count': 3,", "'response_received_count': 30,"),
        ("'item_scraped_count': 2,", "'item_scraped_count': 20,"),
        ("'log_count/ERROR': 5,", "'log_count/ERROR': 4,"),
        ("'finish_reason': 'finished',", "'finish_reason': 'forceshutdown',")
    ]
    dict_count = dict(
        critical_logs=5,
        error_logs=4,
        warning_logs=3,
        redirect_logs=15,
        retry_logs=2,
        ignore_logs=1
    )
    text = END
    for replace in replaces:
        text = text.replace(*replace)
    data = parse(text, headlines=50, taillines=50)
    # cst.json_dumps(data)
    assert data['first_log_time'] == '2018-10-23 18:29:41'
    assert data['latest_log_time'] == '2018-10-23 18:29:42'
    assert data['runtime'] == '0:00:01'
    assert data['datas'] == []
    assert data['pages'] == 30
    assert data['items'] == 20
    for k, v in data['latest_matches'].items():
        assert v == ''
    for k, v in dict_count.items():
        assert data['log_categories'][k]['count'] == v
        assert data['log_categories'][k]['details'] == []
    assert data['finish_reason'] == 'forceshutdown'


# Received SIGTERM twice
def test_shutdown_reason():
    data = parse(SHUTDOWN)
    assert data['shutdown_reason'] == 'Received SIGTERM twice'
    assert data['finish_reason'] == 'shutdown'

    data = parse(SHUTDOWN.replace('twice', ''))
    assert data['shutdown_reason'] == 'Received SIGTERM'
    assert data['finish_reason'] == 'shutdown'

def test_telnet_info():
    data = parse(TELNET_160_DEFAULT)
    d = data['latest_matches']
    assert d['scrapy_version'] == '1.6.0'
    assert d['telnet_console'] == '127.0.0.1:6024'
    assert d['telnet_username'] == ''
    assert d['telnet_password'] == '9d3a29f17ee1bf9a'

    data = parse(TELNET_160_USERNAME)
    d = data['latest_matches']
    assert d['telnet_username'] == 'usr123'
    assert d['telnet_password'] == 'd24ad6be287d69b3'

    data = parse(TELNET_160_PASSWORD)
    d = data['latest_matches']
    assert d['telnet_username'] == ''
    assert d['telnet_password'] == '456psw'

    data = parse(TELNET_160_USERNAME_PASSWORD)
    d = data['latest_matches']
    assert d['telnet_username'] == 'usr123'
    assert d['telnet_password'] == '456psw'
