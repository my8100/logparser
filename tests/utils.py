# coding: utf-8
from datetime import datetime
import io
import json
import os
import platform
from subprocess import Popen
import sys
import time

from logparser import __version__


if len(os.linesep) == 2:
    SIZE = 15862  # In Windows, os.linesep is '\r\n'
else:
    SIZE = 15862 - (180 - 1)  # 180 lines in 2019-01-01T00_00_01.log


class Constant(object):
    ON_WINDOWS = platform.system() == 'Windows'
    PY2 = sys.version_info.major < 3

    NA = 'N/A'
    LOGPARSER_VERSION = __version__
    SIZE = SIZE
    STATUS = 'ok'
    SCRAPYD_SERVER = '127.0.0.1:6800'
    LOG_ENCODING = 'utf-8'
    LOG_EXTENSIONS = ['.log', '.txt']
    LOG_HEAD_LINES = 50
    LOG_TAIL_LINES = 100

    PROJECT = 'demo'
    SPIDER = 'test'
    JOB = '2019-01-01T00_00_01'
    # JOB_KEY = '%s/%s/%s' % (PROJECT, SPIDER, JOB)
    # JOB_TEMP_KEY = JOB_KEY + '_temp'

    PROJECT_TXT = 'demo_txt'
    SPIDER_TXT = 'test_txt'
    JOB_TXT = '2019-01-01T00_00_02'
    # JOB_TXT_KEY = '%s/%s/%s' % (PROJECT_TXT, SPIDER_TXT, JOB_TXT)

    CWD = os.path.dirname(os.path.abspath(__file__))
    LOGS_ZIP_PATH = os.path.join(CWD, 'logs.zip')
    LOGS_PATH = os.path.join(CWD, 'logs')
    LOG_PATH = os.path.join(LOGS_PATH, PROJECT, SPIDER, '%s.log' % JOB)
    LOG_TEMP_PATH = os.path.join(LOGS_PATH, PROJECT, SPIDER, '%s_temp.log' % JOB)
    TXT_PATH = os.path.join(LOGS_PATH, PROJECT_TXT, SPIDER_TXT, '%s.txt' % JOB_TXT)

    DEMO_PROJECT_PATH = os.path.join(CWD, 'demo_project')
    DEMO_PROJECT_LOG_FOLDER_PATH = os.path.join(LOGS_PATH, 'demo_project', 'example')

    LOG_JSON_PATH = os.path.join(LOGS_PATH, PROJECT, SPIDER, '%s.json' % JOB)
    LOG_JSON_TEMP_PATH = os.path.join(LOGS_PATH, PROJECT, SPIDER, '%s_temp.json' % JOB)
    TXT_JSON_PATH = os.path.join(LOGS_PATH, PROJECT_TXT, SPIDER_TXT, '%s.json' % JOB_TXT)

    GBK_LOG_PATH = os.path.join(LOGS_PATH, 'gbk.log')
    STATS_JSON_PATH = os.path.join(LOGS_PATH, 'stats.json')
    DATAS_COMPLETE_JSON_PATH = os.path.join(LOGS_PATH, 'datas_complete.json')
    DATAS_SIMPLIFIED_JSON_PATH = os.path.join(LOGS_PATH, 'datas_simplified.json')
    APPENDED_LOG_PATH = os.path.join(LOGS_PATH, 'appended_log.log')

    PARSE_KEYS = [
        'head',
        'tail',
        'first_log_time',
        'latest_log_time',
        'runtime',
        'first_log_timestamp',
        'latest_log_timestamp',
        'datas',
        'pages',
        'items',
        'latest_matches',
        'latest_crawl_timestamp',
        'latest_scrape_timestamp',
        'log_categories',
        'shutdown_reason',
        'finish_reason',
        'crawler_stats',
        'last_update_time',
        'last_update_timestamp',
        'logparser_version'
    ]

    META_KEYS = [
        'log_path',
        'json_path',
        'json_url',
        'size',
        'position',
        'status',
        '_head'
    ]

    FULL_EXTENDED_KEYS = [
        'crawler_engine',
    ]

    SIMPLIFIED_KEYS = [
        'pages',
        'items',
        'first_log_time',
        'latest_log_time',
        'runtime',
        'shutdown_reason',
        'finish_reason',
        'last_update_time'
    ]

    LATEST_MATCHES_RESULT_DICT = dict(
        scrapy_version='1.5.1',
        telnet_console='127.0.0.1:6023',
        telnet_username='',
        telnet_password='',
        resuming_crawl='Resuming crawl',
        latest_offsite='Filtered offsite request to',
        latest_duplicate='Filtered duplicate request',
        latest_crawl='Crawled (',
        latest_scrape='Scraped from',
        latest_item="{'item': 2}",
        latest_stat='pages/min'
    )

    LOG_CATEGORIES_RESULT_DICT = dict(
        critical_logs=(5, '] CRITICAL:'),
        error_logs=(5, '] ERROR:'),
        warning_logs=(3, '] WARNING:'),
        redirect_logs=(1, ': Redirecting ('),
        retry_logs=(2, 'etrying <GET '),  # DEBUG: Retrying <GET      DEBUG: Gave up retrying <GET
        ignore_logs=(1, 'Ignoring response <')
    )

    @staticmethod
    def json_dumps(obj, sort_keys=False):
        return json.dumps(obj, ensure_ascii=False, indent=4, sort_keys=sort_keys)

    def read_data(self, path):
        with io.open(path, 'r', encoding=self.LOG_ENCODING) as f:
            return json.loads(f.read())

    def write_text(self, path, text, append=False):
        with io.open(path, 'a' if append else 'w', encoding=self.LOG_ENCODING) as f:
            f.write(text)

    @staticmethod
    def string_to_timestamp(string):
        datetime_obj = datetime.strptime(string, '%Y-%m-%d %H:%M:%S')
        return int(time.mktime(datetime_obj.timetuple()))

    @staticmethod
    def timestamp_to_string(timestamp):
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    def sub_process(self, args, block=False, timeout=60):
        proc = Popen(args.split())
        if block:
            # TODO: In PY2: TypeError: communicate() got an unexpected keyword argument 'timeout'
            if self.PY2:
                proc.communicate()
            else:
                proc.communicate(timeout=timeout)
        return proc

    def check_demo_data(self, data, without_stats_dumped=False, modified_logstats=False, log_categories_limit=0):
        # 2018-10-23 18:29:41 [scrapy.core.engine] INFO: Closing spider (finished)
        # 2018-10-23 18:29:41 [scrapy.extensions.feedexport] INFO: Stored jsonlines feed
        if without_stats_dumped:
            assert ('Scrapy 1.5.1 started' in data['head']
                    and 'INFO: Closing spider (finished)' not in data['head']
                    and 'INFO: Stored jsonlines feed' not in data['head']
                    and 'INFO: Spider closed (finished)' not in data['head'])
            assert ('Scrapy 1.5.1 started' not in data['tail']
                    and 'INFO: Closing spider (finished)' in data['tail']
                    and 'INFO: Stored jsonlines feed' in data['tail']
                    and 'INFO: Spider closed (finished)' not in data['tail'])
            assert data['latest_log_time'] == '2018-10-23 18:29:41'
            # assert data['latest_log_timestamp'] == 1540290581
            assert data['runtime'] == '0:01:07'
            assert data['finish_reason'] == self.NA
            assert data['crawler_stats'] == {}
        # 2018-10-23 18:29:42 [scrapy.core.engine] INFO: Spider closed (finished)
        else:
            assert 'Scrapy 1.5.1 started' in data['head'] and 'INFO: Spider closed (finished)' not in data['head']
            assert 'Scrapy 1.5.1 started' not in data['tail'] and 'INFO: Spider closed (finished)' in data['tail']
            assert data['latest_log_time'] == '2018-10-23 18:29:42'
            # assert data['latest_log_timestamp'] == 1540290582
            assert data['runtime'] == '0:01:08'
            assert data['finish_reason'] == 'finished'
            assert data['crawler_stats']['source'] == 'log'

        assert data['first_log_time'] == '2018-10-23 18:28:34'
        # assert data['first_log_timestamp'] == 1540290514

        # Time string extracted from logfile doesnot contains timezone info, so avoid using hard coding timestamp.
        # first_log_timestamp, comes from first_log_time
        assert self.timestamp_to_string(data['first_log_timestamp']) == data['first_log_time']
        assert self.timestamp_to_string(data['latest_log_timestamp']) == data['latest_log_time']

        # "last_update_timestamp": 1546272001,
        # "last_update_time": "2019-01-01 00:00:01", comes from last_update_timestamp
        assert self.string_to_timestamp(data['last_update_time']) == data['last_update_timestamp']

        assert len(data['datas']) == 67
        assert data['datas'][0] == ['2018-10-23 18:28:35', 0, 0, 0, 0]
        if modified_logstats:  # To test update_data_with_crawler_stats()
            assert data['datas'][-1] == ['2018-10-23 18:29:41', 1, 2, 3, 4]
        else:
            assert data['datas'][-1] == ['2018-10-23 18:29:41', 3, 0, 2, 0]
        assert data['pages'] == 3
        assert data['items'] == 2
        for k, v in self.LATEST_MATCHES_RESULT_DICT.items():
            if k in ['telnet_username', 'telnet_password']:
                assert not v
            else:
                assert v in data['latest_matches'][k]

        # "latest_crawl_timestamp": 1540290519, comes from ['latest_matches']['latest_crawl'][:19]
        # "latest_scrape_timestamp": 1540290519, comes from ['latest_matches']['latest_scrape'][:19]
        for k in ['latest_crawl', 'latest_scrape']:
            assert self.timestamp_to_string(data['%s_timestamp' % k]) == data['latest_matches'][k][:19]

        for k, (count, keyword) in self.LOG_CATEGORIES_RESULT_DICT.items():
            for detail in data['log_categories'][k]['details']:
                assert keyword in detail
            assert data['log_categories'][k]['count'] == count
            # 'count' would exclude: 'DEBUG: Retrying <GET'
            # 'details' would include: 'DEBUG: Gave up retrying <GET'
            actual_count = 3 if k == 'retry_logs' else count
            expect_count = actual_count if log_categories_limit == 0 else min(log_categories_limit, actual_count)
            assert len(data['log_categories'][k]['details']) == expect_count
            # Ensure the last N but not the first N is kept, see test_log_categories_limit()
            # 2018-10-23 18:28:35 [test] ERROR: error
            # ...
            # 2018-10-23 18:29:41 [scrapy.core.scraper] ERROR: Error downloading
            if k == 'error_logs':
                assert '2018-10-23 18:29:41 [scrapy.core.scraper] ERROR' in data['log_categories'][k]['details'][-1]
        assert data['shutdown_reason'] == self.NA


cst = Constant()

SETTINGS = dict(
    scrapyd_server=cst.SCRAPYD_SERVER,
    scrapyd_logs_dir=cst.LOGS_PATH,  # ''
    parse_round_interval=0,  # 10
    enable_telnet=True,
    override_telnet_console_host='',
    log_encoding=cst.LOG_ENCODING,
    log_extensions=cst.LOG_EXTENSIONS,
    log_head_lines=cst.LOG_HEAD_LINES,  # 100 => 50, 180 lines in total
    log_tail_lines=cst.LOG_TAIL_LINES,  # 200 => 100
    log_categories_limit=10,  # 10
    jobs_to_keep=100,
    chunk_size=10 * 1000 * 1000,  # 10 MB
    delete_existing_json_files_at_startup=False,
    keep_data_in_memory=False,
    # verbose=True,
    verbose=False,
    main_pid=0,
    debug=True,  # False
    exit_timeout=0.001  # 0
)
