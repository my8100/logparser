# coding: utf8
import re


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

# 2019-01-01 00:00:01 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
# {'downloader/exception_count': 3,
LATEST_MATCHES_PATTERN_DICT = dict(
    resuming_crawl=r'Resuming[ ]crawl',          # Resuming crawl (675840 requests scheduled)
    latest_offsite=r'Filtered[ ]offsite',        # Filtered offsite request to 'www.baidu.com'
    latest_duplicate=r'Filtered[ ]duplicate',    # Filtered duplicate request: <GET http://httpbin.org/headers>
    latest_crawl=r'Crawled[ ]\(\d+\)',           # Crawled (200) <GET http://httpbin.org/headers> (referer: None)
    latest_scrape=r'Scraped[ ]from[ ]<',         # Scraped from <200 http://httpbin.org/headers>
    latest_item=r'^\{.+\}',                      # {'item': 1}  TODO: multilines item
    latest_stat=r'Crawled[ ]\d+[ ]pages[ ]\(at'  # Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
)
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

STATS_DUMPED_PATTERN_DICT = dict(
    critical_logs=r"'log_count/CRITICAL'",
    error_logs=r"'log_count/ERROR'",
    warning_logs=r"'log_count/WARNING'",
    # redirect_logs= , use RESPONSE_STATUS_REDIRECT_PATTERN instead
    retry_logs=r"'retry/count'",
    ignore_logs=r"'httperror/response_ignored_count'",
)

# 2019-01-01 00:00:01 [scrapy.core.engine] INFO: Closing spider (finished)
# 2019-01-01 00:00:01 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
# {'downloader/exception_count': 3,
# }
# 2019-01-01 00:00:01 [scrapy.core.engine] INFO: Spider closed (finished)
PATTERN_LOG_ENDING = re.compile(r"""
                                %s[ ][^\n]+?
                                (Dumping[ ]Scrapy[ ]stats:.*?\{.+?\}.*
                                |INFO:[ ]Spider[ ]closed.*)
                                """ % DATETIME_PATTERN, re.X | re.S)


class Constant(object):

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
    STATS_DUMPED_PATTERN_DICT = STATS_DUMPED_PATTERN_DICT
    PATTERN_LOG_ENDING = PATTERN_LOG_ENDING
