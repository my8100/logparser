# coding: utf8
import json
import platform
import sys
try:
    from urllib import urlencode
    from urllib2 import urlopen
except ImportError:
    from urllib.parse import urlencode
    from urllib.request import urlopen

from .__version__ import __version__
from .settings import (SCRAPYD_SERVER, SCRAPYD_LOGS_DIR, PARSE_ROUND_INTERVAL, LOG_ENCODING, LOG_EXTENSIONS,
                       LOG_HEAD_LINES, LOG_TAIL_LINES, DELETE_EXISTING_JSON_FILES_AT_STARTUP,
                       KEEP_DATA_IN_MEMORY, JOBS_TO_KEEP, CHUNK_SIZE, VERBOSE)


custom_settings = dict(
    scrapyd_server=SCRAPYD_SERVER,
    scrapyd_logs_dir=SCRAPYD_LOGS_DIR,
    parse_round_interval=PARSE_ROUND_INTERVAL,
    log_encoding=LOG_ENCODING,
    log_extensions=LOG_EXTENSIONS,
    log_head_lines=LOG_HEAD_LINES,
    log_tail_lines=LOG_TAIL_LINES,
    delete_existing_json_files_at_startup=DELETE_EXISTING_JSON_FILES_AT_STARTUP,
    keep_data_in_memory=KEEP_DATA_IN_MEMORY,
    jobs_to_keep=JOBS_TO_KEEP,
    chunk_size=CHUNK_SIZE,
    verbose=VERBOSE,
    # main_pid=0,
    # debug=False,
    # exit_timeout=0
)


def printf(value, warn=False):
    prefix = "!!!" if warn else ">>>"
    print("%s %s" % (prefix, value))


def check_update():
    js = {}
    try:
        data = dict(custom_settings)
        data['os'] = platform.platform()
        data['py'] = '.'.join([str(n) for n in sys.version_info[:3]])
        data['logparser'] = __version__
        if sys.version_info.major >= 3:
            data = urlencode(data).encode('utf-8', 'replace')
        else:
            data = urlencode(data)
        req = urlopen('https://kaisla.top/update.php', data=data, timeout=3)
        text = req.read().decode('utf-8', 'replace')
        js = json.loads(text)
    # except Exception as err:
        # print(err)
    except:
        pass
    else:
        if js.get('latest_version') == __version__:
            printf('Running the latest version: %s' % __version__)
        else:
            if js.get('info', ''):
                printf(js['info'], warn=True)
            if js.get('force_update', ''):
                sys.exit('Please update and then restart logparser.')
    return js  # For test
