# coding: utf-8
from collections import OrderedDict
from datetime import datetime
import glob
import io
import json
import logging
import os
import platform
import re
import sys
from telnetlib import DO, DONT, IAC, SB, SE, Telnet, TTYPE, WILL, WONT
import time
import traceback

try:
    from psutil import pid_exists
except ImportError:
    pid_exists = None
try:
    from scrapy import __version__ as scrapy_version
except ImportError:
    scrapy_version = '1.0.0'

from . import SETTINGS_PY_PATH
from .__version__ import __version__
from .common import Common
from .scrapylogparser import parse
from .utils import custom_settings, get_logger


logger = get_logger(__name__)

SUPPORTED_SCRAPY_VERSION = '1.5.1'
IN_WINDOWS = True if platform.system() == 'Windows' else False
SIMPLIFIED_KEYS = [
    'log_path',
    'json_path',
    'json_url',
    'size',
    'position',
    'status',
    '_head',

    'pages',
    'items',
    'first_log_time',
    'latest_log_time',
    'runtime',
    'shutdown_reason',
    'finish_reason',
    'last_update_time'
]


# noinspection PyBroadException
class LogParser(Common):
    # datas = {}  # Cause shared self.datas between test functions!
    logger = logger

    def __init__(self, scrapyd_server, scrapyd_logs_dir, parse_round_interval, enable_telnet,
                 override_telnet_console_host, log_encoding, log_extensions, log_head_lines, log_tail_lines,
                 delete_existing_json_files_at_startup, keep_data_in_memory, jobs_to_keep, chunk_size, verbose,
                 main_pid=0, debug=False, exit_timeout=0):
        self.SCRAPYD_SERVER = scrapyd_server
        self.SCRAPYD_LOGS_DIR = scrapyd_logs_dir
        self.PARSE_ROUND_INTERVAL = parse_round_interval
        if enable_telnet and scrapy_version > SUPPORTED_SCRAPY_VERSION:
            self.ENABLE_TELNET = False
            self.logger.warning("ENABLE_TELNET is set to False for unsupported version of Scrapy: %s > %s",
                                scrapy_version, SUPPORTED_SCRAPY_VERSION)
        else:
            self.ENABLE_TELNET = enable_telnet
        self.tn = None

        self.OVERRIDE_TELNET_CONSOLE_HOST = override_telnet_console_host
        self.LOG_ENCODING = log_encoding
        self.LOG_EXTENSIONS = log_extensions
        self.LOG_HEAD_LINES = log_head_lines
        self.LOG_TAIL_LINES = log_tail_lines
        self.DELETE_EXISTING_JSON_FILES_AT_STARTUP = delete_existing_json_files_at_startup
        self.KEEP_DATA_IN_MEMORY = keep_data_in_memory
        self.JOBS_TO_KEEP = jobs_to_keep
        self.CHUNK_SIZE = chunk_size

        self.verbose = verbose
        if self.verbose:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.WARNING)
        self.DEBUG = debug
        self.EXIT_TIMEOUT = exit_timeout

        self.main_pid = main_pid
        self.logparser_pid = os.getpid()

        # TypeError: Object of type set is not JSON serializable
        self.logger.info(self.json_dumps(vars(self)))

        self.stats_json_url = 'http://%s/logs/stats.json' % self.SCRAPYD_SERVER
        self.logparser_version = __version__
        self.init_time = time.time()
        self.log_paths = []
        self.existing_file_keys = set()
        self.datas = {}

        if self.DELETE_EXISTING_JSON_FILES_AT_STARTUP:
            self.delete_existing_results()

        if not os.path.exists(os.path.join(self.SCRAPYD_LOGS_DIR, 'stats.json')):
            self.save_text_into_logs_dir('stats.json', self.json_dumps(self.get_default_stats()))

    def calc_runtime(self, start_string, end_string):
        try:
            start_datetime = datetime.strptime(start_string, '%Y-%m-%d %H:%M:%S')
            end_datetime = datetime.strptime(end_string, '%Y-%m-%d %H:%M:%S')
        except (TypeError, ValueError):  # 0 or ''
            return self.NA
        else:
            return str(end_datetime - start_datetime)

    # REF: /scrapydweb/scrapydweb/utils/poll.py
    def check_exit(self):
        exit_condition_1 = pid_exists is not None and not pid_exists(self.main_pid)
        exit_condition_2 = not IN_WINDOWS and not self.check_pid(self.main_pid)
        if exit_condition_1 or exit_condition_2:
            sys.exit("!!! LogParser subprocess (pid: %s) exits "
                     "since main_pid %s not exists" % (self.logparser_pid, self.main_pid))

    @staticmethod
    def check_pid(pid):
        """ Check For the existence of a unix pid. """
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        else:
            return True

    def count_actual_lines(self, text):
        return len(re.split(self.LINESEP_BULK_PATTERN, text))

    def cut_text(self, text, lines_limit, keep_head=True):
        count = 0
        lines = []
        for line in re.split(self.LINESEP_PATTERN, text)[::1 if keep_head else -1]:
            lines.append(line)
            if line.strip():
                count += 1
            if count == lines_limit:
                break
        return '\n'.join(lines[::1 if keep_head else -1])

    def delete_existing_results(self):
        for path in glob.glob(os.path.join(self.SCRAPYD_LOGS_DIR, '*/*/*.json')):
            try:
                os.remove(path)
            except Exception as err:
                self.logger.error(err)
            else:
                self.logger.warning("Deleted %s", path)

    def find_text_to_ignore(self, text):
        lines = re.split(r'\n', text)  # KEEP the same '\n'
        m = re.search(self.PATTERN_LOG_ENDING, text)
        if m:
            self.logger.info("Found log ending:%s", self.format_log_block('log ending', m.group()))
            text_to_ignore = ''
        else:
            # To ensure the integrity of a log with multilines, e.g. error with traceback info,
            # the tail of the appended_log must be ignored
            # 2019-01-01 00:00:01 [test] WARNING: warning  # Would be parsed in this round
            # 123abc                                       # Would be parsed in this round
            # -------------------------------------------------------------------------
            # 2019-01-01 00:00:01 [test] ERROR: error      # Would be ignored for next round
            # 456abc                                       # Would be ignored for next round
            if len(re.findall(self.DATETIME_PATTERN + r'[ ].+?\n', text)) < 2:
                text_to_ignore = text
                self.logger.debug("Skip short appended log for next round: %s", repr(text_to_ignore))
            else:
                lines_to_ignore = []
                for line in lines[::-1]:
                    lines_to_ignore.append(line)
                    if re.match(self.DATETIME_PATTERN, line):
                        break
                text_to_ignore = '\n'.join(lines_to_ignore[::-1])  # KEEP the same '\n'
                self.logger.debug("Text to be ignored for next round: %s", repr(text_to_ignore))

        return text_to_ignore

    @staticmethod
    def format_log_block(title, log, lines_limit=0):
        if lines_limit:
            lines = re.split(r'\n', log)
            half = max(1, int(lines_limit / 2))
            if len(lines) > lines_limit:
                log = '\n'.join(lines[:half] + ['......'] + lines[-half:])
        return u'\n\n{title}:\n{sign}\n{log}\n{sign}\n'.format(title=title, log=log, sign='='*150)

    def get_default_stats(self):
        last_update_timestamp = int(time.time())
        last_update_time = datetime.fromtimestamp(last_update_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        return dict(status='ok', datas={}, settings_py=self.handle_slash(SETTINGS_PY_PATH), settings=custom_settings,
                    last_update_timestamp=last_update_timestamp, last_update_time=last_update_time,
                    logparser_version=self.logparser_version)

    def handle_logfile(self, log_path):
        self.logger.debug("log_path: %s", log_path)
        project, spider, job, ext = self.parse_log_path(log_path)
        self.existing_file_keys.add(log_path)

        # The last modification time of Scrapy log does not change over time?!
        # mtime = os.path.getmtime(log_path)
        # datetime.fromtimestamp(os.path.getmtime(log_path)).strftime('%Y-%m-%dT%H_%M_%S')
        size = os.path.getsize(log_path)

        if log_path not in self.datas:
            self.logger.warning("New logfile found: %s (%s bytes)", log_path, size)
            json_path = os.path.join(self.SCRAPYD_LOGS_DIR, project, spider, '%s.json' % job)
            json_url = 'http://%s/logs/%s/%s/%s.json' % (self.SCRAPYD_SERVER, project, spider, job)
            # NOTE: do not use handle_slash() on log_path, since parse_log_path() use os.sep
            data = OrderedDict(log_path=log_path, json_path=json_path, json_url=json_url,
                               size=size, position=0, status='ok', _head='')
            self.datas[log_path] = data

            loaded_data = self.read_data(json_path)
            if loaded_data.get('size', -1) == size:
                data.update(loaded_data)  # AVOID using data =
                self.logger.warning("New logfile and its data with same size found: %s (size: %s) -> skip",
                                    json_path, loaded_data['size'])
                return
            else:
                self.logger.warning("New logfile: %s (%s bytes) -> parse", log_path, size)
        elif size < self.datas[log_path]['size']:
            self.logger.warning("Old logfile with smaller size: %s (before: %s, now: %s bytes) -> parse in next round",
                                log_path, self.datas[log_path]['size'], size)
            self.datas.pop(log_path)
            return
        elif size == self.datas[log_path]['size']:
            self.logger.debug("Old logfile with old size: %s (%s bytes) -> skip", log_path, size)
            return
        else:
            self.logger.warning("Old logfile with new size: %s (%s bytes) -> parse", log_path, size)
            data = self.datas[log_path]

            if not self.KEEP_DATA_IN_MEMORY:
                # If the json file is broken, the logfile should be reparsed from position 0
                loaded_data = self.read_data(data['json_path'])
                if (loaded_data.get('size', -1) == data['size']
                   and loaded_data.get('position', -1) == data['position']):
                    data.update(loaded_data)
                else:
                    self.logger.warning("The logfile would be parsed from position 0: %s", log_path)
                    data['position'] = 0
                    data.pop('first_log_time', None)  # See parse_appended_log()
            data['size'] = size

        # f.read(1000000) => f.tell() 15868     # safe
        # f.seek(1000000) => f.tell() 1000000   # unexpected
        # Add max() for logfile with 0 size
        for __ in range(data['position'], max(1, data['size']), self.CHUNK_SIZE):
            self.logger.info("Remaining size to be read: %s bytes", data['size'] - data['position'])
            appended_log = self.read_appended_log(data, size=self.CHUNK_SIZE)
            if self.DEBUG:
                self.save_text_into_logs_dir('appended_log.log', appended_log)
            self.parse_appended_log(data, appended_log)

        return data

    @staticmethod
    def handle_slash(string):
        if not string:
            return string
        else:
            return string.replace('\\', '/')

    def handle_telnet(self, data):
        data.setdefault('crawler_engine', {})
        if (self.ENABLE_TELNET
           and data['latest_matches']['telnet_console']
           and not data['crawler_stats']):  # Do not telnet when the job is finished
            try:
                self.telnet(data)
            except:
                self.logger.error(traceback.format_exc())
            finally:
                if self.tn is not None:
                    try:
                        self.tn.close()
                    except:
                        pass

    @staticmethod
    def json_dumps(obj, sort_keys=False):
        return json.dumps(obj, ensure_ascii=False, indent=4, sort_keys=sort_keys)

    @staticmethod
    def json_dump(obj, f, sort_keys=False):
        json.dump(obj, f, ensure_ascii=False, indent=4, sort_keys=sort_keys)

    def main(self):
        while True:
            if self.main_pid:
                self.check_exit()
            start_time = time.time()
            try:
                self.run()
                end_time = time.time()
                self.logger.debug("Took %.1f seconds this round", (end_time - start_time))
                if 0 < self.EXIT_TIMEOUT < end_time - self.init_time:
                    self.logger.critical("GoodBye, EXIT_TIMEOUT: %s", self.EXIT_TIMEOUT)
                    break
                else:
                    self.logger.warning("Sleep %s seconds", self.PARSE_ROUND_INTERVAL)
                    time.sleep(self.PARSE_ROUND_INTERVAL)
            except KeyboardInterrupt:
                if self.main_pid:
                    self.logger.warning("LogParser subprocess (pid: %s) cancelled by KeyboardInterrupt",
                                        self.logparser_pid)
                else:
                    self.logger.warning("KeyboardInterrupt")
                sys.exit()
            except:
                self.logger.error(traceback.format_exc())

    def parse_appended_log(self, data, appended_log):
        tail_backup = data.get('tail', '')
        # Note that appended_log may be an empty string
        data_ = parse(appended_log, self.LOG_HEAD_LINES, self.LOG_TAIL_LINES)
        self.logger.debug("Parsed data_ from appended_log:\n%s", self.json_dumps(data_))

        if 'first_log_time' not in data:
            # To keep the order of keys in Python 2
            for k, v in data_.items():
                data[k] = v
        else:
            # data['head'] would be updated below
            data['tail'] = data_['tail']

            if data['first_log_time'] == self.NA:
                data['first_log_time'] = data_['first_log_time']
                data['first_log_timestamp'] = data_['first_log_timestamp']
            if data_['latest_log_time'] != self.NA:
                data['latest_log_time'] = data_['latest_log_time']
                data['latest_log_timestamp'] = data_['latest_log_timestamp']
            data['runtime'] = self.calc_runtime(data['first_log_time'], data['latest_log_time'])

            data['datas'].extend(data_['datas'])
            for k in ['pages', 'items']:
                if data[k] is None:
                    data[k] = data_[k]
                elif data_[k] is not None:
                    data[k] = max(data[k], data_[k])

            for k, v in data_['latest_matches'].items():
                data['latest_matches'][k] = v or data['latest_matches'][k]
            # latest_crawl_timestamp, latest_scrape_timestamp
            for k in ['latest_crawl', 'latest_scrape']:
                if data_['latest_matches'][k]:
                    data['%s_timestamp' % k] = data_['%s_timestamp' % k]

            # "log_categories": {"critical_logs": {"count": 0, "details": []}}
            for k, v in data_['log_categories'].items():
                if v['count'] > 0:
                    if data_['finish_reason'] != self.NA:
                        data['log_categories'][k]['count'] = v['count']
                    else:
                        data['log_categories'][k]['count'] += v['count']
                data['log_categories'][k]['details'].extend(v['details'])

            for k in ['shutdown_reason', 'finish_reason']:
                if data_[k] != self.NA:
                    data[k] = data_[k]
            data['crawler_stats'] = data_['crawler_stats'] or data['crawler_stats']
            data['last_update_timestamp'] = data_['last_update_timestamp']
            data['last_update_time'] = data_['last_update_time']

        # To ensure the actual length of headlines and taillines
        if data['_head'] != self.LOG_HEAD_LINES:
            if data['_head']:
                if appended_log:
                    data['head'] = '%s\n%s' % (data['_head'], appended_log)
                else:  # appended_log would be empty string for short appended log
                    data['head'] = data['_head']
            else:
                data['head'] = appended_log
            data['head'] = self.cut_text(data['head'], self.LOG_HEAD_LINES)
            if self.count_actual_lines(data['head']) < self.LOG_HEAD_LINES:
                data['_head'] = data['head']
            else:
                data['_head'] = self.LOG_HEAD_LINES

        if self.count_actual_lines(data['tail']) < self.LOG_TAIL_LINES:
            if tail_backup:
                if appended_log:
                    data['tail'] = '%s\n%s' % (tail_backup, appended_log)
                else:
                    data['tail'] = tail_backup
            else:
                data['tail'] = appended_log
        data['tail'] = self.cut_text(data['tail'], self.LOG_TAIL_LINES, keep_head=False)

        self.logger.info("crawled_pages %s, scraped_items %s", data['pages'], data['items'])

    @staticmethod
    def parse_log_path(log_path):
        project, spider, _job = log_path.split(os.sep)[-3:]
        job, ext = os.path.splitext(_job)  # ('job', '') or ('job', '.log')
        return project, spider, job, ext

    def read_appended_log(self, data, size=-1, backoff_times=10):
        # If the argument size is omitted, None, or negative, reads and returns all data until EOF.
        # https://stackoverflow.com/a/21533561/10517783
        # In text files (those opened without a b in the mode string),
        # only seeks relative to the beginning of the file are allowed
        # b'\x80abc'.decode('utf-8')
        # UnicodeDecodeError: 'utf-8' codec can't decode byte 0x80 in position 0: invalid start byte
        size_backup = size
        text = ''
        with io.open(data['log_path'], 'rb') as f:
            f.seek(data['position'])
            for count in range(1, backoff_times + 1):
                try:
                    text = f.read(size).decode(self.LOG_ENCODING, 'strict')
                except UnicodeDecodeError as err:
                    self.logger.error(err)
                    if count == backoff_times:
                        self.logger.critical("Use f.read().decode(%s, 'replace') instead.", self.LOG_ENCODING)
                        f.seek(data['position'])
                        text = f.read(size_backup).decode(self.LOG_ENCODING, 'replace')
                    else:
                        # A backoff of 1 byte every time
                        size = f.tell() - data['position'] - 1
                        if size > 0:
                            f.seek(data['position'])
                            self.logger.warning("Fail %s times, backoff to %s and read %s bytes", count, f.tell(), size)
                else:
                    break
            current_stream_position = f.tell()

        text_to_ignore = self.find_text_to_ignore(text)
        if text_to_ignore == text:
            return ''
        else:
            data['position'] = current_stream_position - len(text_to_ignore.encode(self.LOG_ENCODING))
            appended_log = text[:-len(text_to_ignore)] if text_to_ignore else text
            self.logger.info("Found appended log:%s",
                             self.format_log_block('appended log', appended_log, lines_limit=10))
            return appended_log

    def read_data(self, json_path):
        data = {}
        self.logger.info("Try to load json file: %s", json_path)
        if not os.path.exists(json_path):
            self.logger.warning("Json file not found: %s", json_path)
        else:
            try:
                with io.open(json_path, 'r', encoding='utf-8') as f:
                    data = json.loads(f.read())
            except Exception as err:
                self.logger.error(err)
            else:
                self.logger.debug("Loaded json file: %s", json_path)
                logparser_version = data.get('logparser_version', '')
                if logparser_version != __version__:
                    data = {}
                    self.logger.warning("Ignore json file for mismatching version : %s", logparser_version)
        return data

    def run(self):
        self.log_paths = []
        for ext in self.LOG_EXTENSIONS:
            self.log_paths.extend(glob.glob(os.path.join(self.SCRAPYD_LOGS_DIR, '*/*/*%s' % ext)))
        self.logger.info("Found %s logfiles", len(self.log_paths))

        self.existing_file_keys = set()
        for log_path in self.log_paths:
            try:
                data = self.handle_logfile(log_path)
                if not data:
                    continue
                self.handle_telnet(data)
                self.save_data(data)
            except:
                self.logger.error(traceback.format_exc())
                self.logger.warning("Pop %s from self.datas", log_path)
                self.datas.pop(log_path, None)

        if self.DEBUG:
            self.save_text_into_logs_dir('datas_complete.json', self.json_dumps(self.datas))
        self.simplify_datas_in_memory()
        if self.DEBUG:
            self.save_text_into_logs_dir('datas_simplified.json', self.json_dumps(self.datas))
        self.save_datas()

    def save_data(self, data):
        with io.open(data['json_path'], 'w') as f:
            self.json_dump(data, f)
        self.logger.warning("Saved to %s", data['json_path'])

    def save_datas(self):
        stats = self.get_default_stats()
        for log_path, data in self.datas.items():
            if self.KEEP_DATA_IN_MEMORY and log_path in self.existing_file_keys:
                data = self.simplify_data(dict(data))
            else:
                data = dict(data)
            data.pop('_head')  # To simplify data for 'List Stats' in the Overview page
            project, spider, job, ext = self.parse_log_path(log_path)
            stats['datas'].setdefault(project, {})
            stats['datas'][project].setdefault(spider, {})
            stats['datas'][project][spider][job] = data
        text = self.json_dumps(stats)
        self.save_text_into_logs_dir('stats.json', text)
        self.logger.warning("Saved to %s", self.stats_json_url)
        self.logger.debug("stats.json: \n%s", text)

    def save_text_into_logs_dir(self, filename, text):
        path = os.path.join(self.SCRAPYD_LOGS_DIR, filename)
        with io.open(path, 'wb') as f:
            content = text.encode('utf-8', 'replace')
            f.write(content)
            self.logger.info("Saved to %s (%s bytes)", filename, len(content))

    @staticmethod
    def simplify_data(data):
        data_ = OrderedDict()
        for k in SIMPLIFIED_KEYS:
            data_[k] = data[k]
        return data_

    def simplify_datas_in_memory(self):
        all_keys = set(self.datas.keys())
        redundant_keys = all_keys.difference(self.existing_file_keys)
        self.logger.info("all_keys: %s", len(all_keys))
        self.logger.info("existing_file_keys: %s", len(self.existing_file_keys))
        self.logger.info("redundant_keys: %s", len(redundant_keys))
        if self.KEEP_DATA_IN_MEMORY:
            keys_to_simplify = redundant_keys
        else:
            keys_to_simplify = all_keys
        for key in keys_to_simplify:
            if 'head' not in self.datas[key]:  # Has been simplified
                continue
            self.logger.debug("Simplify %s in memory", key)
            self.datas[key] = self.simplify_data(self.datas[key])
        self.logger.info("Datas in memory: ")
        for key, value in self.datas.items():
            self.logger.info("%s: %s keys, size %s", key, len(value), sys.getsizeof(value))

        # Remove data of deleted log to reduce the size of the stats.json file
        if len(all_keys) > self.JOBS_TO_KEEP and redundant_keys:
            self.logger.info("JOBS_TO_KEEP: %s", self.JOBS_TO_KEEP)
            self.logger.info("Limit the size of all_keys in memory: %s", len(all_keys))
            for key in redundant_keys:
                self.datas.pop(key)
                self.logger.debug("Pop key: %s", key)
            self.logger.info("Now all_keys in memory: %s", len(self.datas))
        else:
            self.logger.info("all_keys in memory: %s", len(self.datas))

    # Note that the telnet feature is tested in test_telnet_in_stats() by ScrapydWeb
    # https://stackoverflow.com/questions/18547412/python-telnetlib-to-connect-to-scrapy-telnet-to-read-stats
    def telnet(self, data):
        # Telnet console listening on 127.0.0.1:6023
        m = re.search(r'listening[ ]on[ ](.+):(\d+)$', data['latest_matches']['telnet_console'])
        if not m:
            self.logger.warning("Fail to extract host and port from %s", data['latest_matches']['telnet_console'])
            return
        host, port = m.groups()
        host = self.OVERRIDE_TELNET_CONSOLE_HOST or host
        self.logger.debug("Try to telnet to %s:%s for %s", host, port, data['log_path'])
        try:
            self.tn = Telnet(host, int(port), timeout=10)
        # except ConnectionRefusedError as err:  # Python 2: <class 'socket.error'>
        except Exception as err:
            self.logger.error("Fail to telnet to %s:%s for %s: %s", host, port, data['log_path'], err)
            return

        if self.verbose:
            self.tn.set_debuglevel(logging.DEBUG)
        # [twisted] CRITICAL: Unhandled Error
        # Failure: twisted.conch.telnet.OptionRefused: twisted.conch.telnet.OptionRefused
        # https://github.com/jookies/jasmin-web/issues/2
        self.tn.set_option_negotiation_callback(self.telnet_callback)

        # spider._job, spider._version, settings.attributes["BOT_NAME"].value, JOB, SPIDER, PROJECT
        # '\'logs\\\\demo_persistent\\\\test\\\\2019-01-23T18_25_34.log\'\r\r\r\n>>>'
        _log_file = self.telnet_io(b'settings.attributes["LOG_FILE"].value', return_text=True)
        self.logger.debug("settings['LOG_FILE'] found via telnet: %s", _log_file)
        # Username: Password:
        if 'Username:' in _log_file:
            self.logger.error("The feature of collecting crawler_stats and crawler_engine via telnet "
                              "temporarily only works for Scrapy 1.5.1 and its earlier version: %s", _log_file)
            return
        for part in self.parse_log_path(data['log_path']):
            if part not in _log_file:
                self.logger.warning("%s not found in settings['LOG_FILE']: %s", part, _log_file)
                return

        data['crawler_stats'] = self.telnet_io(b'stats.get_stats()') or data['crawler_stats']
        if data['crawler_stats']:
            # update_log_count=False to avoid wrong count in parse_appended_log() when the job is running
            self.update_data_with_crawler_stats(data, data['crawler_stats'], update_log_count=False)
        data['crawler_engine'] = self.telnet_io(b'est()') or data['crawler_engine']

        self.logger.debug("crawler_stats:\n%s", self.json_dumps(data['crawler_stats']))
        self.logger.debug("crawler_engine:\n%s", self.json_dumps(data['crawler_engine']))

    @staticmethod
    def telnet_callback(tn, command, option):
        if command == DO and option == TTYPE:
            tn.sendall(IAC + WILL + TTYPE)
            tn.sendall(IAC + SB + TTYPE + '\0' + 'LogParser' + IAC + SE)
        elif command in (DO, DONT):
            tn.sendall(IAC + WILL + option)
        elif command in (WILL, WONT):
            tn.sendall(IAC + DO + option)

    def telnet_io(self, command, return_text=False):
        # Microsoft Telnet> o
        # ( to )127.0.0.1 6023
        # >>>stats.get_stats()
        # >>>est()
        self.tn.write(b'%s\n' % command)
        content = self.tn.read_until(b'\n>>>', timeout=10)
        # print(repr(content))
        # b"\x1bc>>> \x1b[4hstats.get_stats()\r\r\r\n{'log_count/INFO': 61,
        # 'start_time': datetime.datetime(2019, 1, 22, 9, 7, 14, 998126),
        # 'httperror/response_ignored_status_count/404': 1}\r\r\r\n>>>"
        # b' est()\r\r\r\nExecution engine status\r\r\r\n\r\r\r\n
        # time()-engine.start_time                        : 3249.7548048496246
        # engine.scraper.slot.needs_backout()             : False\r\r\r\n\r\r\r\n\r\r\r\n>>>'
        text = content.decode('utf-8')
        if return_text:
            return text
        m = re.search(r'{.+}', text)
        if m:
            result = self.parse_crawler_stats(m.group())
        else:
            lines = [line for line in re.split(r'\r\n|\n|\r', text) if ':' in line]
            result = dict([re.split(r'\s*:\s*', line, maxsplit=1) for line in lines])
            for k, v in result.items():
                if k == 'engine.spider.name':
                    continue
                elif v == 'True':
                    result[k] = True
                elif v == 'False':
                    result[k] = False
                else:
                    try:
                        result[k] = int(float(v))
                    except (TypeError, ValueError):
                        pass

        if result:
            return self.get_ordered_dict(result, source='telnet')
        else:
            return {}
