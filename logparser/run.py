# coding: utf-8
import argparse
import os
import sys
import time

from . import SETTINGS_PY_PATH
from .__version__ import __description__, __url__, __version__
from .logparser import LogParser
from .utils import check_update, custom_settings, get_logger


logger = get_logger('logparser.run')  # __name__

STAR = '\n%s\n' % ('*' * 100)


def main():
    logger.info("LogParser version: %s", __version__)
    logger.info("Use 'logparser -h' to get help")
    logger.info("Main pid: %s", os.getpid())
    logger.info("Check out the config file below for more advanced settings.")
    print(u"{star}Loading settings from {path}{star}".format(star=STAR, path=SETTINGS_PY_PATH.replace('\\', '/')))
    args = parse_args()
    # "logparser -h" ends up here
    try:
        update_config(args)
    except AssertionError as err:
        logger.error("Check config fail: ")
        sys.exit(u"\n{err}\nCheck and update your settings in {path}\n".format(
            err=err, path=SETTINGS_PY_PATH.replace('\\', '/')))
    print("{star}Visit stats at: http://{server}/logs/stats.json{star}".format(
        star=STAR, server=custom_settings['scrapyd_server']))
    # if not custom_settings.get('main_pid', 0):
    check_update()
    logparser = LogParser(**custom_settings)
    time.sleep(3)
    logparser.main()


def parse_args():
    parser = argparse.ArgumentParser(description="LogParser -- %s\nGitHub: %s" % (__description__, __url__))

    scrapyd_server = custom_settings.get('scrapyd_server', '') or '127.0.0.1:6800'
    parser.add_argument(
        '-ss', '--scrapyd_server',
        default=scrapyd_server,
        help=("current: {server}, e.g. 127.0.0.1:6800, the stats of Scrapyd jobs can be accessed at: "
              "http://{server}/logs/stats.json").format(server=scrapyd_server)
    )

    scrapyd_logs_dir = custom_settings.get('scrapyd_logs_dir', '') or os.path.join(os.path.expanduser('~'), 'logs')
    parser.add_argument(
        '-dir', '--scrapyd_logs_dir',
        default=scrapyd_logs_dir,
        help=("current: %s, e.g. C:/Users/username/logs/ or /home/username/logs/, "
              "Check out this link to find out where the Scrapy logs are stored: "
              "https://scrapyd.readthedocs.io/en/stable/config.html#logs-dir") % scrapyd_logs_dir
    )

    parse_round_interval = custom_settings.get('parse_round_interval', 10)
    parser.add_argument(
        '-t', '--sleep',
        default=parse_round_interval,
        help="current: %s, sleep N seconds before starting next round of parsing logs." % parse_round_interval
    )

    enable_telnet = custom_settings.get('enable_telnet', True)
    parser.add_argument(
        '-dt', '--disable_telnet',
        action='store_true',
        help=("current: ENABLE_TELNET = %s, append '--disable_telnet' to disable collecting "
              "Crawler.stats and Crawler.engine via telnet") % enable_telnet
    )

    delete_existing_json_files_at_startup = custom_settings.get('delete_existing_json_files_at_startup', True)
    parser.add_argument(
        '-del', '--delete_json_files',
        action='store_true',
        help=("current: DELETE_EXISTING_JSON_FILES_AT_STARTUP = %s, append '--delete_json_files' "
              "to delete existing parsed results at startup" % delete_existing_json_files_at_startup)
    )

    verbose = custom_settings.get('verbose', False)
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help=("current: VERBOSE = %s, append '--verbose' to set the logging level to DEBUG "
              "for getting more information about how LogParser works") % verbose
    )

    parser.add_argument(
        '--main_pid',
        default=0,
        help="current: 0, reserved for running as a subprocess of ScrapydWeb, just ignore this argument"
    )

    return parser.parse_args()


def update_config(args):
    logger.debug("Reading settings from command line: %s", args)
    logger.debug("Checking config")

    custom_settings['scrapyd_server'] = args.scrapyd_server
    logger.info("SCRAPYD_SERVER: %s", custom_settings['scrapyd_server'])

    scrapyd_logs_dir = args.scrapyd_logs_dir
    assert os.path.isdir(scrapyd_logs_dir), "SCRAPYD_LOGS_DIR not found: %s" % repr(scrapyd_logs_dir)

    custom_settings['scrapyd_logs_dir'] = scrapyd_logs_dir
    logger.info("SCRAPYD_LOGS_DIR: %s", custom_settings['scrapyd_logs_dir'])

    parse_round_interval = args.sleep
    try:
        # ValueError: invalid literal for int() with base 10: '0.1'
        assert int(parse_round_interval) >= 0
    except (TypeError, ValueError, AssertionError):  # [], ''
        assert False, "PARSE_ROUND_INTERVAL should be a non-negative integer: %s" % repr(parse_round_interval)
    custom_settings['parse_round_interval'] = int(parse_round_interval)
    logger.info("PARSE_ROUND_INTERVAL: %s", custom_settings['parse_round_interval'])

    # action='store_true': default False
    if args.disable_telnet:
        custom_settings['enable_telnet'] = False
    logger.info("ENABLE_TELNET: %s", custom_settings['enable_telnet'])

    if args.delete_json_files:
        custom_settings['delete_existing_json_files_at_startup'] = True
    logger.info("DELETE_EXISTING_JSON_FILES_AT_STARTUP: %s", custom_settings['delete_existing_json_files_at_startup'])

    if args.verbose:
        custom_settings['verbose'] = True
    logger.info("VERBOSE: %s", custom_settings['verbose'])

    main_pid = args.main_pid
    try:
        assert int(main_pid) >= 0
    except (TypeError, ValueError, AssertionError):  # [], ''
        assert False, "main_pid should be a non-negative integer: %s" % repr(main_pid)
    custom_settings['main_pid'] = int(main_pid)
    if custom_settings['main_pid']:
        logger.info("main_pid: %s", custom_settings['main_pid'])


if __name__ == '__main__':
    main()
