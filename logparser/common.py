# coding: utf-8
from collections import OrderedDict
import json
from datetime import datetime
import os
import platform
import sys
import re
import time
import traceback


CWD = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PY_PATH = os.path.join(CWD, 'settings.py')

# LINESEP_PATTERN = re.compile(r'%s' % os.linesep)
LINESEP_PATTERN = re.compile(r'\r\n|\n|\r')
LINESEP_BULK_PATTERN = re.compile(r'(?:\r\n|\n|\r)\s*')  # \s includes <space>\t\r\n\f\v

# 2019-01-01 00:00:01
DATETIME_PATTERN = r'\d{4}-\d{2}-\d{2}[ ]\d{2}:\d{2}:\d{2}'  # <space> would be ignore with re.X, use [ ] instead

# 2019-01-01 00:00:01 [scrapy.extensions.logstats] INFO:
# Crawled 2318 pages (at 2 pages/min), scraped 68438 items (at 60 items/min)
DATAS_PATTERN = re.compile(r"""\n
                            (?P<time_>%s)[ ].+?
                            Crawled[ ](?P<pages>\d+)[ ]pages[ ]\(at[ ](?P<pages_min>\d+)[ ]pages/min\)
                            ,[ ]scraped[ ](?P<items>\d+)[ ]items[ ]\(at[ ](?P<items_min>\d+)[ ]items/min\)
                            """ % DATETIME_PATTERN, re.X)

LOG_CATEGORIES_PATTERN_DICT = dict(
    critical_logs=r'\][ ]CRITICAL:',            # [test] CRITICAL:
    error_logs=r'\][ ]ERROR:',                  # [test] ERROR:
    warning_logs=r'\][ ]WARNING:',              # [test] WARNING:
    redirect_logs=r':[ ]Redirecting[ ]\(',      # DEBUG: Redirecting (302) to <GET
    retry_logs=r'[ ][Rr]etrying[ ]<',           # DEBUG: Retrying <GET      DEBUG: Gave up retrying <GET
    ignore_logs=r':[ ]Ignoring[ ]response[ ]<'  # INFO: Ignoring response <404
)
for k, v in LOG_CATEGORIES_PATTERN_DICT.items():
    p = re.compile(r"""\n
                    ({time_}[ ][^\n]+?{pattern}.*?)                                  # first line (and its details)
                    (?=\r?\n{time_}[ ][^\n]+?(?:DEBUG|INFO|WARNING|ERROR|CRITICAL))  # ?=: Would not consume strings
                   """.format(time_=DATETIME_PATTERN, pattern=v), re.X | re.S)       # re.S: . matches new line
    LOG_CATEGORIES_PATTERN_DICT[k] = p
_odict = OrderedDict()
for k in ['critical_logs', 'error_logs', 'warning_logs', 'redirect_logs', 'retry_logs', 'ignore_logs']:
    _odict.update({k: LOG_CATEGORIES_PATTERN_DICT[k]})
LOG_CATEGORIES_PATTERN_DICT = _odict

# 2019-01-01 00:00:01 [scrapy.extensions.telnet] DEBUG: Telnet console listening on 127.0.0.1:6023
# 2019-01-01 00:00:01 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
# {'downloader/exception_count': 3,
LATEST_MATCHES_PATTERN_DICT = dict(
    scrapy_version=r'Scrapy[ ]\d+\.\d+\.\d+[ ]started',    # Scrapy 1.5.1 started (bot: demo)
    telnet_console=r'Telnet[ ]console[ ]listening[ ]on',   # Telnet console listening on 127.0.0.1:6023
    # Default: 'scrapy' | Overridden settings: {'TELNETCONSOLE_USERNAME': 'usr'}
    telnet_username=r'Overridden[ ]settings:.+TELNETCONSOLE_USERNAME',
    # Telnet Password: 865bba341ef25552 | Overridden settings: {'TELNETCONSOLE_PASSWORD': 'psw'}
    telnet_password=r'Overridden[ ]settings:.+TELNETCONSOLE_PASSWORD|Telnet[ ]Password:[ ].+',
    resuming_crawl=r'Resuming[ ]crawl',          # Resuming crawl (675840 requests scheduled)
    latest_offsite=r'Filtered[ ]offsite',        # Filtered offsite request to 'www.baidu.com'
    latest_duplicate=r'Filtered[ ]duplicate',    # Filtered duplicate request: <GET http://httpbin.org/headers>
    latest_crawl=r'Crawled[ ]\(\d+\)',           # Crawled (200) <GET http://httpbin.org/headers> (referer: None)
    latest_scrape=r'Scraped[ ]from[ ]<',         # Scraped from <200 http://httpbin.org/headers>
    latest_item=r'^\{.+\}',                      # {'item': 1}  TODO: multilines item
    latest_stat=r'Crawled[ ]\d+[ ]pages[ ]\(at'  # Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
)
_odict = OrderedDict()
for k in ['scrapy_version', 'telnet_console', 'telnet_username', 'telnet_password', 'resuming_crawl',
          'latest_offsite', 'latest_duplicate', 'latest_crawl', 'latest_scrape', 'latest_item', 'latest_stat']:
    _odict.update({k: LATEST_MATCHES_PATTERN_DICT[k]})
LATEST_MATCHES_PATTERN_DICT = _odict
for k, v in LATEST_MATCHES_PATTERN_DICT.items():
    if k != 'latest_item':
        LATEST_MATCHES_PATTERN_DICT[k] = r'^%s[ ].+?%s' % (DATETIME_PATTERN, v)

# 2019-01-01 00:00:01 [scrapy.crawler] INFO: Received SIGTERM, shutting down gracefully. Send again to force
# 2019-01-01 00:00:01 [scrapy.core.engine] INFO: Closing spider (shutdown)
# 2019-01-01 00:00:01 [scrapy.crawler] INFO: Received SIGTERM twice, forcing unclean shutdown
SIGTERM_PATTERN = re.compile(r'^%s[ ].+?:[ ](Received[ ]SIGTERM([ ]twice)?),' % DATETIME_PATTERN)

# 'downloader/response_status_count/200': 2,
# 200 301 302 401 403 404 500 503
RESPONSE_STATUS_PATTERN = re.compile(r"'downloader/response_status_count/\d{3}':[ ](?P<count>\d+),")
RESPONSE_STATUS_REDIRECT_PATTERN = re.compile(r"'downloader/response_status_count/3\d{2}':[ ](?P<count>\d+),")

STATS_DUMPED_CATEGORIES_DICT = dict(
    critical_logs='log_count/CRITICAL',
    error_logs='log_count/ERROR',
    warning_logs='log_count/WARNING',
    # redirect_logs= ,
    retry_logs='retry/count',
    ignore_logs='httperror/response_ignored_count',
)

# 2019-01-01 00:00:01 [scrapy.core.engine] INFO: Closing spider (finished)
# 2019-01-01 00:00:01 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
# {'downloader/exception_count': 3,
# }
# 2019-01-01 00:00:01 [scrapy.core.engine] INFO: Spider closed (finished)
PATTERN_LOG_ENDING = re.compile(r"""
                                (%s)[ ][^\n]+?
                                (Dumping[ ]Scrapy[ ]stats:.*?(\{.+?\}).*
                                |INFO:[ ]Spider[ ]closed.*)
                                """ % DATETIME_PATTERN, re.X | re.S)


class Common(object):
    NA = 'N/A'

    LINESEP_PATTERN = LINESEP_PATTERN
    LINESEP_BULK_PATTERN = LINESEP_BULK_PATTERN

    DATETIME_PATTERN = DATETIME_PATTERN
    DATAS_PATTERN = DATAS_PATTERN
    LOG_CATEGORIES_PATTERN_DICT = LOG_CATEGORIES_PATTERN_DICT
    LATEST_MATCHES_PATTERN_DICT = LATEST_MATCHES_PATTERN_DICT

    SIGTERM_PATTERN = SIGTERM_PATTERN
    RESPONSE_STATUS_PATTERN = RESPONSE_STATUS_PATTERN
    RESPONSE_STATUS_REDIRECT_PATTERN = RESPONSE_STATUS_REDIRECT_PATTERN
    STATS_DUMPED_CATEGORIES_DICT = STATS_DUMPED_CATEGORIES_DICT
    PATTERN_LOG_ENDING = PATTERN_LOG_ENDING

    CWD = CWD
    ON_WINDOWS = platform.system() == 'Windows'
    PY2 = sys.version_info.major < 3
    SETTINGS_PY_PATH = SETTINGS_PY_PATH

    @staticmethod
    def get_current_time_timestamp():
        current_timestamp = int(time.time())
        current_time = datetime.fromtimestamp(current_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        return current_time, current_timestamp

    @staticmethod
    def parse_log_path(log_path):
        project, spider, _job = log_path.split(os.sep)[-3:]
        job, ext = os.path.splitext(_job)  # ('job', '') or ('job', '.log')
        return project, spider, job, ext

    def get_ordered_dict(self, adict, source):
        odict = OrderedDict(source=source)
        odict['last_update_time'], odict['last_update_timestamp'] = self.get_current_time_timestamp()
        for key in sorted(adict.keys()):
            odict[key] = adict[key]
        return odict

    @staticmethod
    def parse_crawler_stats(text):
        # 'start_time': datetime.datetime(2019, 3, 9, 13, 55, 24, 601697)
        # "robotstxt/exception_count/<class 'twisted.internet.error.TCPTimedOutError'>": 1,
        # scrapy-crawlera/scrapy_crawlera/middleware.py:
            # self.crawler.stats.inc_value(
                # 'crawlera/response/error/%s' % crawlera_error.decode('utf8'))
        # u"crawlera/response/error/timeout": 1
        backup = text
        text = re.sub(r'(datetime.datetime\(.+?\))', r'"\1"', text)
        text = re.sub(r'(".*?)\'(.*?)\'(.*?")', r'\1_\2_\3', text)
        text = re.sub(r"'(.+?)'", r'"\1"', text)
        text = re.sub(r'[bu]"(.+?)"', r'"\1"', text)
        try:
            return json.loads(text)
        except ValueError as err:
            print(text)
            print(traceback.format_exc())
            return dict(json_loads_error=err, stats=backup)

    def update_data_with_crawler_stats(self, data, crawler_stats, update_log_count):
        # 'downloader/response_count': 4,
        # 'downloader/response_status_count/200': 2,
        # 'downloader/response_status_count/302': 1,
        # 'downloader/response_status_count/404': 1,
        # 'finish_reason': 'closespider_timeout',
        # 'item_scraped_count': 2,
        # 'response_received_count': 3,
        data['finish_reason'] = crawler_stats.get('finish_reason', data['finish_reason'])
        data['pages'] = crawler_stats.get('response_received_count', data['pages'])
        data['items'] = crawler_stats.get('item_scraped_count', data['items'])

        if not update_log_count:
            return
        redirect_count = 0
        for key, value in crawler_stats.items():
            if key.startswith('downloader/response_status_count/3'):
                redirect_count += value
        if redirect_count > 0:
            data['log_categories']['redirect_logs']['count'] = redirect_count

        for level, key in self.STATS_DUMPED_CATEGORIES_DICT.items():
            count = crawler_stats.get(key, 0)
            if count > 0:
                data['log_categories'][level]['count'] = count
