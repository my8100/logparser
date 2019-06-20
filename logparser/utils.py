# coding: utf-8
import json
import logging
import platform
import sys

try:
    from scrapy import __version__ as scrapy_version
except ImportError:
    scrapy_version = '0.0.0'
from six.moves.urllib.parse import urlencode
from six.moves.urllib.request import urlopen

from .__version__ import __version__
from .settings import (SCRAPYD_SERVER, SCRAPYD_LOGS_DIR, PARSE_ROUND_INTERVAL,
                       ENABLE_TELNET, OVERRIDE_TELNET_CONSOLE_HOST, LOG_ENCODING, LOG_EXTENSIONS,
                       LOG_HEAD_LINES, LOG_TAIL_LINES, LOG_CATEGORIES_LIMIT, JOBS_TO_KEEP, CHUNK_SIZE,
                       DELETE_EXISTING_JSON_FILES_AT_STARTUP, KEEP_DATA_IN_MEMORY, VERBOSE)


custom_settings = dict(
    scrapyd_server=SCRAPYD_SERVER,
    scrapyd_logs_dir=SCRAPYD_LOGS_DIR,
    parse_round_interval=PARSE_ROUND_INTERVAL,
    enable_telnet=ENABLE_TELNET,
    override_telnet_console_host=OVERRIDE_TELNET_CONSOLE_HOST,
    log_encoding=LOG_ENCODING,
    log_extensions=LOG_EXTENSIONS,
    log_head_lines=LOG_HEAD_LINES,
    log_tail_lines=LOG_TAIL_LINES,
    log_categories_limit=LOG_CATEGORIES_LIMIT,
    jobs_to_keep=JOBS_TO_KEEP,
    chunk_size=CHUNK_SIZE,
    delete_existing_json_files_at_startup=DELETE_EXISTING_JSON_FILES_AT_STARTUP,
    keep_data_in_memory=KEEP_DATA_IN_MEMORY,
    verbose=VERBOSE,
    # main_pid=0,
    # debug=False,
    # exit_timeout=0
)


def get_logger(name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt="[%(asctime)s] %(levelname)-8s in %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def check_update(timeout=5):
    logger = get_logger(__name__)
    js = {}
    try:
        data = dict(custom_settings)
        data['os'] = platform.platform()
        data['py'] = '.'.join([str(n) for n in sys.version_info[:3]])
        data['logparser'] = __version__
        data['scrapy_version'] = scrapy_version
        if sys.version_info.major >= 3:
            data = urlencode(data).encode('utf-8', 'replace')
        else:
            data = urlencode(data)
        req = urlopen('https://my8100.herokuapp.com/check_update', data=data, timeout=timeout)
        text = req.read().decode('utf-8', 'replace')
        js = json.loads(text)
        # print(js)
    # except Exception as err:
        # print(err)
    except:
        pass
    else:
        if js.get('latest_version') == __version__:
            logger.info("Running the latest version: %s", __version__)
        else:
            if js.get('info', ''):
                logger.warning(js['info'])
            if js.get('force_update', ''):
                sys.exit("Please update and then restart logparser. ")
    return js  # For test only
