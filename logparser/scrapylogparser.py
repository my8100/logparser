# coding: utf-8
from collections import OrderedDict
from datetime import datetime
import re
import time

from .__version__ import __version__
from .common import Common


def parse(text, headlines=100, taillines=200):
    """Parse the content of a Scrapy logfile and return an OrderedDict object.

    :param text: content to be parsed, in unicode.
    :param headlines: (optional) extracted the first N lines, the default is 100.
    :param taillines: (optional) extracted the last N lines, the default is 200.
    :return: an OrderedDict object
    :rtype: collections.OrderedDict

    Usage::

      >>> from logparser import parse
      >>> d = parse(u'The content of a Scrapy logfile, in unicode.')
    """
    return ScrapyLogParser(text, headlines, taillines).main()


# noinspection PyTypeChecker
class ScrapyLogParser(Common):

    def __init__(self, text, headlines=100, taillines=200):
        text = text.strip()
        self.data = OrderedDict()
        self.lines = re.split(self.LINESEP_PATTERN, text)
        self.data['head'] = '\n'.join(self.lines[:headlines])
        self.data['tail'] = '\n'.join(self.lines[-taillines:])
        # Modify text for self.DATAS_PATTERN, self.LOG_CATEGORIES_PATTERN_DICT
        self.text = '\n%s\n2019-01-01 00:00:01 [] DEBUG' % text

    def main(self):
        self.extract_time()
        self.extract_datas()
        self.extract_latest_matches()
        self.extract_log_categories()
        self.extract_shutdown_reason()
        self.extract_stats_dumped()
        self.data['last_update_time'], self.data['last_update_timestamp'] = self.get_current_time_timestamp()
        self.data['logparser_version'] = __version__
        return self.data

    def re_search_final_match(self, pattern, default='', step=-1):
        for line in self.lines[::step]:
            if re.search(pattern, line):
                return line
        return default

    @staticmethod
    def string_to_datetime_obj(string):
        return datetime.strptime(string, '%Y-%m-%d %H:%M:%S')

    @staticmethod
    def datetime_obj_to_timestamp(datetime_obj):
        """
        :param datetime_obj: datetime.datetime
        :rtype: int object
        """
        return int(time.mktime(datetime_obj.timetuple()))

    def extract_time(self):
        self.data['first_log_time'] = self.re_search_final_match(r'^%s[ ]' % self.DATETIME_PATTERN, step=1)[:19]
        self.data['latest_log_time'] = self.re_search_final_match(r'^%s[ ]' % self.DATETIME_PATTERN)[:19]

        if self.data['first_log_time'] and self.data['latest_log_time']:
            first_log_datetime = self.string_to_datetime_obj(self.data['first_log_time'])
            latest_log_datetime = self.string_to_datetime_obj(self.data['latest_log_time'])
            self.data['runtime'] = str(latest_log_datetime - first_log_datetime)
            self.data['first_log_timestamp'] = self.datetime_obj_to_timestamp(first_log_datetime)
            self.data['latest_log_timestamp'] = self.datetime_obj_to_timestamp(latest_log_datetime)
        else:
            self.data['first_log_time'] = self.NA
            self.data['latest_log_time'] = self.NA
            self.data['runtime'] = self.NA
            self.data['first_log_timestamp'] = 0
            self.data['latest_log_timestamp'] = 0

    # Extract datas for chart
    def extract_datas(self):
        datas = re.findall(self.DATAS_PATTERN, self.text)
        # For compatibility with Python 2, str(time_) to avoid [u'2019-01-01 00:00:01', 0, 0, 0, 0] in JavaScript
        self.data['datas'] = [[str(time_), int(pages), int(pages_min), int(items), int(items_min)]
                              for (time_, pages, pages_min, items, items_min) in datas]
        # TODO: Crawled (200) <GET,     Scraped from <200
        self.data['pages'] = None
        self.data['items'] = None
        if self.data['datas']:
            self.data['pages'] = max(i[1] for i in self.data['datas'])
            self.data['items'] = max(i[3] for i in self.data['datas'])

    def extract_latest_matches(self):
        self.data['latest_matches'] = OrderedDict()
        for k, v in self.LATEST_MATCHES_PATTERN_DICT.items():
            if k in ['scrapy_version', 'telnet_console', 'telnet_username', 'telnet_password', 'resuming_crawl']:
                step = 1
            else:
                step = -1
            result = self.re_search_final_match(v, step=step)
            if result:
                if k == 'scrapy_version':
                    m = re.search(r'Scrapy[ ](\d+\.\d+\.\d+)[ ]started', result)
                    result = m.group(1) if m else ''
                elif k == 'telnet_console':
                    m = re.search(r'listening[ ]on[ ](.+)$', result)
                    result = m.group(1) if m else ''
                elif k == 'telnet_username':
                    m = re.search(r"""TELNETCONSOLE_USERNAME['"]:[ ](['"])(.+?)\1""", result)
                    result = m.group(2) if m else ''
                elif k == 'telnet_password':
                    m = re.search(r'(Telnet[ ]Password:[ ])(.+)', result)
                    m = m or re.search(r"""TELNETCONSOLE_PASSWORD['"]:[ ](['"])(.+?)\1""", result)
                    result = m.group(2) if m else ''
            self.data['latest_matches'][k] = result

        # Scrapyd in PY2: u"{u'Chinese \\u6c49\\u5b57 1':"
        latest_item = self.data['latest_matches']['latest_item']
        if '\\u' in latest_item:  # and sys.version_info.major < 3:
            try:
                self.data['latest_matches']['latest_item'] = latest_item.encode('utf-8').decode('unicode-escape')
            except:
                pass
        # latest_crawl_timestamp, latest_scrape_timestamp
        for k in ['latest_crawl', 'latest_scrape']:
            time_string = self.data['latest_matches'][k][:19]
            if time_string:
                datetime_obj = self.string_to_datetime_obj(time_string)
                self.data['%s_timestamp' % k] = self.datetime_obj_to_timestamp(datetime_obj)
            else:
                self.data['%s_timestamp' % k] = 0

    def extract_log_categories(self):
        self.data['log_categories'] = OrderedDict()
        for level, pattern in self.LOG_CATEGORIES_PATTERN_DICT.items():
            matches = re.findall(pattern, self.text)
            # DEBUG: Gave up retrying <GET
            if level == 'retry_logs' and matches:
                count = len([i for i in matches if 'Gave up retrying <' not in i])
            else:
                count = len(matches)
            self.data['log_categories'][level] = dict(count=count, details=matches)

    def extract_shutdown_reason(self):
        m = re.search(self.SIGTERM_PATTERN, self.re_search_final_match(self.SIGTERM_PATTERN))
        self.data['shutdown_reason'] = m.group(1) if m else self.NA

    def extract_stats_dumped(self):
        self.data['finish_reason'] = self.NA  # May be updated in update_data_with_crawler_stats()
        m = re.search(self.PATTERN_LOG_ENDING, self.text)
        if not (m and m.group(3)):
            self.data['crawler_stats'] = {}
        else:
            crawler_stats = self.parse_crawler_stats(m.group(3))
            self.update_data_with_crawler_stats(self.data, crawler_stats, update_log_count=True)
            self.data['crawler_stats'] = self.get_ordered_dict(crawler_stats, source='log')
            time_string = m.group(1)
            datetime_obj = self.string_to_datetime_obj(time_string)
            self.data['crawler_stats']['last_update_time'] = time_string
            self.data['crawler_stats']['last_update_timestamp'] = self.datetime_obj_to_timestamp(datetime_obj)
