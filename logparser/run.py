# coding: utf8
import argparse
import os
import sys

from .__version__ import __version__, __description__
from .logparser import LogParser
from .utils import custom_settings, printf, check_update


CWD = os.path.dirname(os.path.abspath(__file__))
STAR = '*' * 100
SETTINGS_PY_PATH = os.path.join(CWD, 'settings.py')


def main():
    printf("LogParser version: %s" % __version__)
    printf("Use 'logparser -h' to get help")
    printf("Main pid: %s" % os.getpid())
    print(STAR)
    printf("Loading settings from %s" % SETTINGS_PY_PATH, warn=True)
    printf("Check out the config file above for more advanced settings.")
    print(STAR)
    args = parse_args()
    # "logparser -h" ends up here
    try:
        update_config(args)
    except AssertionError as err:
        sys.exit("\n!!! %s\nCheck and update your settings in %s" % (err, SETTINGS_PY_PATH))
    print(STAR)
    printf("Visit stats at: http://%s/logs/stats.json" % custom_settings['scrapyd_server'], warn=True)
    if not custom_settings.get('main_pid', 0):
        check_update()
    print(STAR)
    logparser = LogParser(**custom_settings)
    logparser.main()


def parse_args():
    parser = argparse.ArgumentParser(description='LogParser -- %s' % __description__)

    scrapyd_server = custom_settings.get('scrapyd_server', '') or '127.0.0.1:6800'
    parser.add_argument(
        '-ss', '--scrapyd_server',
        default=scrapyd_server,
        help=("current: {server}, e.g. 127.0.0.1:6800, the stats of Scrapyd jobs can be accessed at: "
              "http://{server}/logs/stats.json").format(server=scrapyd_server)
    )

    scrapyd_logs_dir = custom_settings.get('scrapyd_logs_dir', '') or os.path.join(os.path.expanduser('~'), 'logs')
    parser.add_argument(
        '-dir',
        default=scrapyd_logs_dir,
        help=("current: %s, e.g. C:/Users/username/logs/ or /home/username/logs/, "
              "Check out this link to find out where the Scrapy logs are stored: "
              "https://scrapyd.readthedocs.io/en/stable/config.html#logs-dir") % scrapyd_logs_dir
    )

    parse_round_interval = custom_settings.get('parse_round_interval', 60)
    parser.add_argument(
        '-t', '--sleep',
        default=parse_round_interval,
        help="current: %s, sleep N seconds before starting next round of parsing logs." % parse_round_interval
    )

    delete_existing_json_files_at_startup = custom_settings.get('delete_existing_json_files_at_startup', True)
    parser.add_argument(
        '-del', '--delete_json_files',
        action='store_true',
        help=("current: DELETE_EXISTING_JSON_FILES_AT_STARTUP = %s, append '-del' "
              "to delete existing parsed results at startup" % delete_existing_json_files_at_startup)
    )

    verbose = custom_settings.get('verbose', False)
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help=("current: VERBOSE = %s, append '-v' to set the logging level to DEBUG "
              "for getting more information about how LogParser works") % verbose
    )

    parser.add_argument(
        '--main_pid',
        default=0,
        help="current: 0, reserved for running as a subprocess of ScrapydWeb, just ignore this argument"
    )

    return parser.parse_args()


def update_config(args):
    printf("Reading settings from command line: %s" % args, warn=True)

    custom_settings['scrapyd_server'] = args.scrapyd_server
    printf("SCRAPYD_SERVER: %s" % custom_settings['scrapyd_server'])

    scrapyd_logs_dir = args.dir
    assert os.path.isdir(scrapyd_logs_dir), "SCRAPYD_LOGS_DIR NOT found: %s" % repr(scrapyd_logs_dir)

    custom_settings['scrapyd_logs_dir'] = scrapyd_logs_dir
    printf("SCRAPYD_LOGS_DIR: %s" % custom_settings['scrapyd_logs_dir'])

    parse_round_interval = args.sleep
    try:
        assert int(parse_round_interval) >= 0
    except (TypeError, ValueError, AssertionError):  # [], ''
        assert False, "PARSE_ROUND_INTERVAL should be a non-negative integer: %s" % repr(parse_round_interval)
    custom_settings['parse_round_interval'] = int(parse_round_interval)
    printf("PARSE_ROUND_INTERVAL: %s" % custom_settings['parse_round_interval'])

    # action='store_true': default False
    if args.delete_json_files:
        custom_settings['delete_existing_json_files_at_startup'] = True
    printf("DELETE_EXISTING_JSON_FILES_AT_STARTUP: %s" % custom_settings['delete_existing_json_files_at_startup'])

    if args.verbose:
        custom_settings['verbose'] = True
    printf("VERBOSE: %s" % custom_settings['verbose'])

    main_pid = args.main_pid
    try:
        assert int(main_pid) >= 0
    except (TypeError, ValueError, AssertionError):  # [], ''
        assert False, "main_pid should be a non-negative integer: %s" % repr(main_pid)
    custom_settings['main_pid'] = int(main_pid)
    if custom_settings['main_pid']:
        printf("main_pid: %s" % custom_settings['main_pid'])


if __name__ == '__main__':
    main()
