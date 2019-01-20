# coding: utf8
from collections import OrderedDict
from datetime import datetime
import re
import time

from .constant import Constant


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


class ScrapyLogParser(Constant):

    def __init__(self, text, headlines=100, taillines=200):
        text = text.strip()
        self.data = OrderedDict()
        self.lines = re.split(self.LINESEP_PATTERN, text)
        self.data['head'] = '\n'.join(self.lines[:headlines])
        self.data['tail'] = '\n'.join(self.lines[-taillines:])
        # Modify text for self.DATAS_PATTERN, self.LOG_CATEGORIES_PATTERN_DICT
        self.text = '\n%s\n2019-01-01 00:00:01 DEBUG' % text

    def main(self):
        self.extract_time()
        self.extract_datas()
        self.extract_latest_matches()
        self.extract_log_categories()
        self.extract_shutdown_reason()
        self.extract_stats_dumped()
        self.data['last_update_timestamp'] = int(time.time())
        self.data['last_update_time'] = self.timestamp_to_string(self.data['last_update_timestamp'])
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
        return int(time.mktime(datetime_obj.timetuple()))

    @staticmethod
    def timestamp_to_string(timestamp):
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    def extract_time(self):
        self.data['first_log_time'] = self.re_search_final_match(r'^%s[ ]' % self.DATETIME_PATTERN, step=1)[:19]
        self.data['latest_log_time'] = self.re_search_final_match(r'^%s[ ]' % self.DATETIME_PATTERN)[:19]

        if self.data['first_log_time'] and self.data['latest_log_time']:
            first_log_datetime = self.string_to_datetime_obj(self.data['first_log_time'])
            latest_log_datetime = self.string_to_datetime_obj(self.data['latest_log_time'])
            self.data['elapsed'] = str(latest_log_datetime - first_log_datetime)
            self.data['first_log_timestamp'] = self.datetime_obj_to_timestamp(first_log_datetime)
            self.data['latest_log_timestamp'] = self.datetime_obj_to_timestamp(latest_log_datetime)
        else:
            self.data['first_log_time'] = self.NA
            self.data['latest_log_time'] = self.NA
            self.data['elapsed'] = self.NA
            self.data['first_log_timestamp'] = 0
            self.data['latest_log_timestamp'] = 0

    # Extract datas for chart
    def extract_datas(self):
        datas = re.findall(self.DATAS_PATTERN, self.text)
        # For compatibility with Python 2, str(time_) to avoid [u'2019-01-01 00:00:01', 0, 0, 0, 0] in JavaScript
        self.data['datas'] = [[str(time_), int(pages), int(pages_min), int(items), int(items_min)]
                              for (time_, pages, pages_min, items, items_min) in datas]
        # TODO: Crawled (200) <GET,     Scraped from <200
        self.data['pages'] = int(datas[-1][1]) if datas else 0
        self.data['items'] = int(datas[-1][3]) if datas else 0

    def extract_latest_matches(self):
        self.data['latest_matches'] = {}
        for k, v in self.LATEST_MATCHES_PATTERN_DICT.items():
            self.data['latest_matches'][k] = self.re_search_final_match(v, step=1 if k == 'resuming_crawl' else -1)
        # latest_crawl_timestamp, latest_scrape_timestamp
        for k in ['latest_crawl', 'latest_scrape']:
            time_string = self.data['latest_matches'][k][:19]
            if time_string:
                datetime_obj = self.string_to_datetime_obj(time_string)
                self.data['%s_timestamp' % k] = self.datetime_obj_to_timestamp(datetime_obj)
            else:
                self.data['%s_timestamp' % k] = 0

    def extract_log_categories(self):
        self.data['log_categories'] = {}
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
        # TODO
        # 'finish_time': datetime.datetime(2018, 10, 23, 10, 29, 41, 174719),
        # 'start_time': datetime.datetime(2018, 10, 23, 10, 28, 35, 70938)}

        # 'finish_reason': 'closespider_timeout',
        m = re.search(r":[ ]'(.+?)'", self.re_search_final_match(r"'finish_reason'"))
        self.data['finish_reason'] = m.group(1) if m else self.NA

        if self.data['finish_reason'] != self.NA:
            redirect_count = sum([int(i) for i in re.findall(self.RESPONSE_STATUS_REDIRECT_PATTERN, self.text)])
            if redirect_count > 0:
                self.data['log_categories']['redirect_logs']['count'] = redirect_count

            # 'downloader/response_count': 4,
            # 'downloader/response_status_count/200': 2,
            # 'downloader/response_status_count/302': 1,
            # 'downloader/response_status_count/404': 1,
            # 'response_received_count': 3,
            m = re.search(r":[ ](\d+)", self.re_search_final_match(r"'response_received_count'"))
            self.data['pages'] = (int(m.group(1)) if m else 0) or self.data['pages']

            # 'item_scraped_count': 2,
            m = re.search(r":[ ](\d+)", self.re_search_final_match(r"'item_scraped_count'"))
            self.data['items'] = (int(m.group(1)) if m else 0) or self.data['items']

            for level, pattern in self.STATS_DUMPED_PATTERN_DICT.items():
                m = re.search(r":[ ](\d+)", self.re_search_final_match(pattern))
                if m:
                    self.data['log_categories'][level]['count'] = int(m.group(1))
