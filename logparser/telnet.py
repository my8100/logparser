# coding: utf-8
import io
import logging
import os
import re
import sys
from telnetlib import DO, DONT, IAC, SB, SE, Telnet, TTYPE, WILL, WONT
import traceback

import pexpect

from .common import Common
from .utils import get_logger


logger = get_logger(__name__)

SUPPORTED_SCRAPY_VERSION = '1.5.1'
TELNET_TIMEOUT = 10
TELNET_LOG_FILE = 'telnet_log'
TELNETCONSOLE_DEFAULT_USERNAME = 'scrapy'
TELNETCONSOLE_COMMAND_MAP = dict(
    log_file=b'settings.attributes["LOG_FILE"].value',
    crawler_stats=b'stats.get_stats()',
    crawler_engine=b'est()'
)


# noinspection PyBroadException
class MyTelnet(Common):
    logger = logger

    def __init__(self, data, override_telnet_console_host, verbose):
        self.data = data
        self.OVERRIDE_TELNET_CONSOLE_HOST = override_telnet_console_host
        self.verbose = verbose
        if self.verbose:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.WARNING)

        self.scrapy_version = self.data['latest_matches']['scrapy_version'] or '0.0.0'
        self.telnet_console = self.data['latest_matches']['telnet_console']
        self.telnet_username = self.data['latest_matches']['telnet_username'] or TELNETCONSOLE_DEFAULT_USERNAME
        self.telnet_password = self.data['latest_matches']['telnet_password']
        self.host = None
        self.port = None
        self.tn = None
        self.crawler_stats = {}
        self.crawler_engine = {}

    def main(self):
        try:
            self.run()
        # Cannot catch error directly in setup_pexpect()
        # pexpect.exceptions.EOF: End Of File (EOF). Exception style platform.
        # pexpect.exceptions.TIMEOUT: Timeout exceeded  # Old logfile but connected to 1.5.1
        # except (pexpect.exceptions.EOF, pexpect.exceptions.TIMEOUT) as err:
        # In setup_telnet(): # except ConnectionRefusedError as err:  # Python 2: <class 'socket.error'>
        except Exception as err:
            self.logger.error("Fail to telnet to %s:%s for %s (%s). Maybe the job was stopped: %s",
                              self.host, self.port, self.data['log_path'], self.scrapy_version, err)
            if self.verbose:
                self.logger.error(traceback.format_exc())
        finally:
            if self.tn is not None:
                try:
                    self.tn.close()
                except:
                    pass
            self.tn = None

        return self.crawler_stats, self.crawler_engine

    # https://stackoverflow.com/questions/18547412/python-telnetlib-to-connect-to-scrapy-telnet-to-read-stats
    def run(self):
        self.logger.debug("scrapy_version: %s", self.scrapy_version)
        if self.ON_WINDOWS and self.scrapy_version > SUPPORTED_SCRAPY_VERSION:
            self.logger.error("Telnet only supports scrapy<=%s on Windows, current scrapy_version: %s",
                              SUPPORTED_SCRAPY_VERSION, self.scrapy_version)
            return
        # Telnet console listening on 127.0.0.1:6023
        m = re.search(r'^(.+):(\d+)$', self.telnet_console)
        if not m:
            self.logger.warning("Fail to extract host and port from %s", self.telnet_console)
            return
        self.host, self.port = m.groups()
        self.host = self.OVERRIDE_TELNET_CONSOLE_HOST or self.host

        self.logger.debug("Try to telnet to %s:%s for %s", self.host, self.port, self.data['log_path'])
        if self.telnet_password:
            self.setup_pexpect()
            if self.tn is not None:
                self.pexpect_io()
        else:
            self.setup_telnet()
            if self.tn is not None:
                self.telnet_io()

    def setup_pexpect(self):
        # Cannot catch error directly here, see main()
        self.tn = pexpect.spawn('telnet %s %s' % (self.host, self.port), encoding='utf-8', timeout=TELNET_TIMEOUT)
        # logfile: <open file '<stdout>', mode 'w' at 0x7fe160149150>
        # logfile_read: None
        # logfile_send: None
        if self.verbose:
            self.tn.logfile = sys.stdout
        else:
            self.tn.logfile = io.open(os.path.join(self.CWD, TELNET_LOG_FILE), 'w')

    @staticmethod
    def telnet_callback(tn, command, option):
        if command == DO and option == TTYPE:
            tn.sendall(IAC + WILL + TTYPE)
            tn.sendall(IAC + SB + TTYPE + '\0' + 'LogParser' + IAC + SE)
        elif command in (DO, DONT):
            tn.sendall(IAC + WILL + option)
        elif command in (WILL, WONT):
            tn.sendall(IAC + DO + option)

    def setup_telnet(self):
        self.tn = Telnet(self.host, int(self.port), timeout=TELNET_TIMEOUT)
        # [twisted] CRITICAL: Unhandled Error
        # Failure: twisted.conch.telnet.OptionRefused: twisted.conch.telnet.OptionRefused
        # https://github.com/jookies/jasmin-web/issues/2
        self.tn.set_option_negotiation_callback(self.telnet_callback)
        if self.verbose:
            self.tn.set_debuglevel(logging.DEBUG)

    def parse_output(self, text):
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

    def pexpect_io(self):
        def bytes_to_str(src):
            if self.PY2:
                return src
            return src.decode('utf-8')
        # TypeError: got <type 'str'> ('Username: ') as pattern,
        # must be one of: <type 'unicode'>, pexpect.EOF, pexpect.TIMEOUT
        self.tn.expect(u'Username: ', timeout=TELNET_TIMEOUT)
        self.tn.sendline(self.telnet_username)
        self.tn.expect(u'Password: ', timeout=TELNET_TIMEOUT)
        self.tn.sendline(self.telnet_password)
        self.tn.expect(u'>>>', timeout=TELNET_TIMEOUT)

        self.tn.sendline(bytes_to_str(TELNETCONSOLE_COMMAND_MAP['log_file']))
        self.tn.expect(re.compile(r'[\'"].+>>>', re.S), timeout=TELNET_TIMEOUT)
        log_file = self.tn.after
        self.logger.debug("settings['LOG_FILE'] found via telnet: %s", log_file)
        if not self.verify_log_file_path(self.parse_log_path(self.data['log_path']), log_file):
            self.logger.warning("Skip telnet due to mismatching: %s AND %s", self.data['log_path'], log_file)
            return

        self.tn.sendline(bytes_to_str(TELNETCONSOLE_COMMAND_MAP['crawler_stats']))
        self.tn.expect(re.compile(r'{.+>>>', re.S), timeout=TELNET_TIMEOUT)
        self.crawler_stats = self.parse_output(self.tn.after)

        self.tn.sendline(bytes_to_str(TELNETCONSOLE_COMMAND_MAP['crawler_engine']))
        self.tn.expect(re.compile(r'Execution engine status.+>>>', re.S), timeout=TELNET_TIMEOUT)
        self.crawler_engine = self.parse_output(self.tn.after)

    def _telnet_io(self, command):
        # Microsoft Telnet> o
        # ( to )127.0.0.1 6023
        # >>>stats.get_stats()
        # >>>est()
        self.tn.write(b'%s\n' % command)
        content = self.tn.read_until(b'\n>>>', timeout=TELNET_TIMEOUT)
        # print(repr(content))
        # b"\x1bc>>> \x1b[4hstats.get_stats()\r\r\r\n{'log_count/INFO': 61,
        # 'start_time': datetime.datetime(2019, 1, 22, 9, 7, 14, 998126),
        # 'httperror/response_ignored_status_count/404': 1}\r\r\r\n>>>"
        # b' est()\r\r\r\nExecution engine status\r\r\r\n\r\r\r\n
        # time()-engine.start_time                        : 3249.7548048496246
        # engine.scraper.slot.needs_backout()             : False\r\r\r\n\r\r\r\n\r\r\r\n>>>'
        return content.decode('utf-8')

    def telnet_io(self):
        # spider._job, spider._version, settings.attributes["BOT_NAME"].value, JOB, SPIDER, PROJECT
        # '\'logs\\\\demo_persistent\\\\test\\\\2019-01-23T18_25_34.log\'\r\r\r\n>>>'
        log_file = self._telnet_io(TELNETCONSOLE_COMMAND_MAP['log_file'])
        self.logger.debug("settings['LOG_FILE'] found via telnet: %s", log_file)
        # Username: Password:
        if 'Username:' in log_file:
            self.logger.error("Telnet with auth is not supported on Windows. You can use scrapy<=%s instead: %s",
                              SUPPORTED_SCRAPY_VERSION, log_file)
            return
        if not self.verify_log_file_path(self.parse_log_path(self.data['log_path']), log_file):
            self.logger.warning("Skip telnet due to mismatching: %s vs %s", self.data['log_path'], log_file)
            return
        self.crawler_stats = self.parse_output(self._telnet_io(TELNETCONSOLE_COMMAND_MAP['crawler_stats']))
        self.crawler_engine = self.parse_output(self._telnet_io(TELNETCONSOLE_COMMAND_MAP['crawler_engine']))

    def verify_log_file_path(self, parts, log_file):
        for part in parts:
            if part not in log_file:
                self.logger.warning("%s not found in settings['LOG_FILE']: %s", part, log_file)
                return False
        return True
