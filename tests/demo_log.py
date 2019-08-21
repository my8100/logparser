# coding: utf-8

ERROR_404 = u"""
<html>
  <head><title>404 - No Such Resource</title></head>
  <body>
    <h1>No Such Resource</h1>
    <p>File not found.</p>
  </body>
</html>
"""

SHUTDOWN = u"""2019-01-01 00:00:01 [scrapy.crawler] INFO: Received SIGTERM, shutting down gracefully. Send again to force
2019-01-01 00:00:01 [scrapy.core.engine] INFO: Closing spider (shutdown)
2019-01-01 00:00:01 [scrapy.crawler] INFO: Received SIGTERM twice, forcing unclean shutdown
2019-01-01 00:00:01 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
{
 'finish_reason': 'shutdown',
 "robotstxt/exception_count/<class 'twisted.internet.error.TCPTimedOutError'>": 1,
 'start_time': datetime.datetime(2019, 3, 9, 13, 55, 24, 601697)
}
2019-01-01 00:00:01 [scrapy.core.engine] INFO: Spider closed (finished)"""

TELNET_160_DEFAULT = u"""2019-06-11 15:53:48 [scrapy.utils.log] INFO: Scrapy 1.6.0 started (bot: ScrapydWeb_demo)
2019-06-11 15:53:48 [scrapy.crawler] INFO: Overridden settings: {'BOT_NAME': 'ScrapydWeb_demo', 'FEED_EXPORT_ENCODING': 'utf-8', 'FEED_URI': 'file:///C:/Users/win7/items/ScrapydWeb_demo/test/2019-06-11T15_53_43.jl', 'LOG_FILE': 'logs\\ScrapydWeb_demo\\test\\2019-06-11T15_53_43.log', 'NEWSPIDER_MODULE': 'ScrapydWeb_demo.spiders', 'ROBOTSTXT_OBEY': True, 'SPIDER_MODULES': ['ScrapydWeb_demo.spiders']}
2019-06-11 15:53:48 [scrapy.extensions.telnet] INFO: Telnet Password: 9d3a29f17ee1bf9a
2019-06-11 15:53:49 [scrapy.extensions.telnet] INFO: Telnet console listening on 127.0.0.1:6024
"""

TELNET_160_USERNAME = u"""2019-06-11 16:05:38 [scrapy.utils.log] INFO: Scrapy 1.6.0 started (bot: ScrapydWeb_demo)
2019-06-11 16:05:38 [scrapy.crawler] INFO: Overridden settings: {'BOT_NAME': 'ScrapydWeb_demo', 'FEED_EXPORT_ENCODING': 'utf-8', 'FEED_URI': 'file:///C:/Users/win7/items/ScrapydWeb_demo/test/2019-06-11T16_05_09.jl', 'LOG_FILE': 'logs\\ScrapydWeb_demo\\test\\2019-06-11T16_05_09.log', 'NEWSPIDER_MODULE': 'ScrapydWeb_demo.spiders', 'ROBOTSTXT_OBEY': True, 'SPIDER_MODULES': ['ScrapydWeb_demo.spiders'], 'TELNETCONSOLE_USERNAME': 'usr123'}
2019-06-11 16:05:38 [scrapy.extensions.telnet] INFO: Telnet Password: d24ad6be287d69b3
2019-06-11 16:05:38 [scrapy.extensions.telnet] INFO: Telnet console listening on 127.0.0.1:6024
"""

TELNET_160_PASSWORD = u"""2019-06-11 16:08:44 [scrapy.utils.log] INFO: Scrapy 1.6.0 started (bot: ScrapydWeb_demo)
2019-06-11 16:08:44 [scrapy.crawler] INFO: Overridden settings: {'BOT_NAME': 'ScrapydWeb_demo', 'FEED_EXPORT_ENCODING': 'utf-8', 'FEED_URI': 'file:///C:/Users/win7/items/ScrapydWeb_demo/test/2019-06-11T16_07_57.jl', 'LOG_FILE': 'logs\\ScrapydWeb_demo\\test\\2019-06-11T16_07_57.log', 'NEWSPIDER_MODULE': 'ScrapydWeb_demo.spiders', 'ROBOTSTXT_OBEY': True, 'SPIDER_MODULES': ['ScrapydWeb_demo.spiders'], 'TELNETCONSOLE_PASSWORD': '456psw'}
2019-06-11 16:08:44 [scrapy.extensions.telnet] INFO: Telnet console listening on 127.0.0.1:6024
"""

TELNET_160_USERNAME_PASSWORD = u"""2019-06-11 16:15:13 [scrapy.utils.log] INFO: Scrapy 1.6.0 started (bot: ScrapydWeb_demo)
2019-06-11 16:15:13 [scrapy.crawler] INFO: Overridden settings: {'BOT_NAME': 'ScrapydWeb_demo', 'FEED_EXPORT_ENCODING': 'utf-8', 'FEED_URI': 'file:///C:/Users/win7/items/ScrapydWeb_demo/test/2019-06-11T16_14_36.jl', 'LOG_FILE': 'logs\\ScrapydWeb_demo\\test\\2019-06-11T16_14_36.log', 'NEWSPIDER_MODULE': 'ScrapydWeb_demo.spiders', 'ROBOTSTXT_OBEY': True, 'SPIDER_MODULES': ['ScrapydWeb_demo.spiders'], 'TELNETCONSOLE_PASSWORD': '456psw', 'TELNETCONSOLE_USERNAME': 'usr123'}
2019-06-11 16:15:14 [scrapy.extensions.telnet] INFO: Telnet console listening on 127.0.0.1:6024
"""

TELNET_151_NO_PORT = u"""2019-06-15 11:53:00 [scrapy.utils.log] INFO: Scrapy 1.5.1 started (bot: demo_project)
2019-06-15 11:53:01 [scrapy.extensions.telnet] DEBUG: Telnet console listening on localhost
2019-06-15 11:53:02 [scrapy.extensions.logstats] INFO: Crawled 0 pages (at 0 pages/min), scraped 0 items (at 0 items/min)
"""

TELNET_151_PORT_16023 = u"""2019-06-15 11:53:00 [scrapy.utils.log] INFO: Scrapy 1.5.1 started (bot: demo_project)
2019-06-15 11:53:01 [scrapy.extensions.telnet] DEBUG: Telnet console listening on 127.0.0.1:16023
2019-06-15 11:53:02 [scrapy.extensions.logstats] INFO: Crawled 0 pages (at 0 pages/min), scraped 0 items (at 0 items/min)
"""

TELNET_160_PORT_16024 = u"""2019-06-15 11:53:00 [scrapy.utils.log] INFO: Scrapy 1.6.0 started (bot: demo_project)
2019-06-15 11:53:01 [scrapy.extensions.telnet] INFO: Telnet Password: 9d3a29f17ee1bf9a
2019-06-15 11:53:01 [scrapy.extensions.telnet] DEBUG: Telnet console listening on 127.0.0.1:16024
2019-06-15 11:53:02 [scrapy.extensions.logstats] INFO: Crawled 0 pages (at 0 pages/min), scraped 0 items (at 0 items/min)
"""

LATEST_SCRAPE_ITEM_ONE_LINE = u"""2019-01-01 00:00:01 [scrapy.core.scraper] DEBUG: Scraped from <200 http://httpbin.org/get>
{'item': 1}
"""

LATEST_SCRAPE_ITEM_MULTIPLE_LINES = u"""2019-01-01 00:00:02 [scrapy.core.scraper] DEBUG: Scraped from <200 http://httpbin.org/get>
{
    'item': 2
}
"""

LATEST_SCRAPE_ITEM_MIXED = u"""2019-01-01 00:00:01 [scrapy.core.scraper] DEBUG: Scraped from <200 http://httpbin.org/get>
{'item': 1}
2019-01-01 00:00:03 [scrapy.core.scraper] DEBUG: Scraped from <200 http://httpbin.org/get>
{
    'item': {
        u'Chinese \u6c49\u5b57': 3
    }
}
2019-01-01 00:00:04 [scrapy_fieldstats.fieldstats] INFO: Field stats:
{'item': '100%'}
2019-01-01 00:00:04 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
"""

SCRAPY_FIELDSTATS = u"""2019-01-01 00:00:01 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
{'dupefilter/filtered': 1,
 'fields_coverage': {
                        u'Chinese \u6c49\u5b57': '50%',
                        'author': {
                            'a': 1,
                            'b': 2
                        }
                    },
 'finish_reason': 'finished'}
"""

FRONT = u"""2018-10-23 18:28:34 [scrapy.utils.log] INFO: Scrapy 1.5.1 started (bot: demo)
2018-10-23 18:28:34 [scrapy.utils.log] INFO: Versions: lxml 4.2.1.0, libxml2 2.9.7, cssselect 1.0.3, parsel 1.4.0, w3lib 1.19.0, Twisted 17.5.0, Python 3.6.5 |Anaconda, Inc.| (default, Mar 29 2018, 13:32:41) [MSC v.1900 64 bit (AMD64)], pyOpenSSL 17.5.0 (OpenSSL 1.0.2o  27 Mar 2018), cryptography 2.2.1, Platform Windows-7-6.1.7601-SP1
2018-10-23 18:28:34 [scrapy.crawler] INFO: Overridden settings: {'BOT_NAME': 'demo', 'CONCURRENT_REQUESTS': 2, 'COOKIES_ENABLED': False, 'DOWNLOAD_DELAY': 1, 'FEED_URI': 'file:///C:/Users/win7/items/demo/test/2018-10-23_182826.jl', 'LOGSTATS_INTERVAL': 1, 'LOG_FILE': 'logs/demo/test/2018-10-23_182826.log', 'NEWSPIDER_MODULE': 'demo.spiders', 'SPIDER_MODULES': ['demo.spiders'], 'USER_AGENT': 'Mozilla/5.0'}
2018-10-23 18:28:34 [scrapy.middleware] INFO: Enabled extensions:
['scrapy.extensions.corestats.CoreStats',
 'scrapy.extensions.telnet.TelnetConsole',
 'scrapy.extensions.feedexport.FeedExporter',
 'scrapy.extensions.logstats.LogStats']
2018-10-23 18:28:35 [scrapy.middleware] INFO: Enabled downloader middlewares:
['scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware',
 'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware',
 'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware',
 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware',
 'scrapy.downloadermiddlewares.retry.RetryMiddleware',
 'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware',
 'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware',
 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware',
 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware',
 'scrapy.downloadermiddlewares.stats.DownloaderStats']
2018-10-23 18:28:35 [scrapy.middleware] INFO: Enabled spider middlewares:
['scrapy.spidermiddlewares.httperror.HttpErrorMiddleware',
 'scrapy.spidermiddlewares.offsite.OffsiteMiddleware',
 'scrapy.spidermiddlewares.referer.RefererMiddleware',
 'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware',
 'scrapy.spidermiddlewares.depth.DepthMiddleware']
2018-10-23 18:28:35 [scrapy.middleware] INFO: Enabled item pipelines:
[]
2018-10-23 18:28:35 [scrapy.core.engine] INFO: Spider opened
2018-10-23 18:28:35 [scrapy.extensions.logstats] INFO: Crawled 0 pages (at 0 pages/min), scraped 0 items (at 0 items/min)
2018-10-23 18:28:35 [scrapy.extensions.telnet] DEBUG: Telnet console listening on 127.0.0.1:6023
2018-10-23 18:28:35 [test] DEBUG: test utf8: 测试中文
2018-10-23 18:28:35 [test] DEBUG: 2018-08-20 09:13:06 [apps_redis] DEBUG: Resuming crawl (675840 requests scheduled)
2018-10-23 18:28:35 [test] WARNING: warn
2018-10-23 18:28:35 [test] ERROR: error
2018-10-23 18:28:35 [test] WARNING: warning
123abc
2018-10-23 18:28:35 [test] ERROR: error
456abc
2018-10-23 18:28:35 [test] ERROR: error
456abc
2018-10-23 18:28:35 [test] CRITICAL: critical
789abc
2018-10-23 18:28:35 [test] WARNING: warning
 123
abc
2018-10-23 18:28:35 [test] ERROR: error
 456
abc
2018-10-23 18:28:35 [test] CRITICAL: critical
2018-10-23 18:28:35 [test] CRITICAL: critical
 789
abc
2018-10-23 18:28:35 [test] CRITICAL: critical
2018-10-23 18:28:35 [test] CRITICAL: critical
2018-10-23 18:28:35 [scrapy.downloadermiddlewares.redirect] DEBUG: Redirecting (302) to <GET http://httpbin.org/get> from <GET http://httpbin.org/redirect/1>
2018-10-23 18:28:36 [scrapy.extensions.logstats] INFO: Crawled 0 pages (at 0 pages/min), scraped 0 items (at 0 items/min)
2018-10-23 18:28:36 [scrapy.core.engine] DEBUG: Crawled (404) <GET http://httpbin.org/status/404> (referer: None)
2018-10-23 18:28:36 [scrapy.spidermiddlewares.httperror] INFO: Ignoring response <404 http://httpbin.org/status/404>: HTTP status code is not handled or not allowed
2018-10-23 18:28:37 [scrapy.extensions.logstats] INFO: Crawled 1 pages (at 60 pages/min), scraped 0 items (at 0 items/min)
2018-10-23 18:28:37 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://httpbin.org/get> (referer: None)
2018-10-23 18:28:37 [scrapy.dupefilters] DEBUG: Filtered duplicate request: <GET http://httpbin.org/headers> - no more duplicates will be shown (see DUPEFILTER_DEBUG to show all duplicates)
2018-10-23 18:28:37 [scrapy.spidermiddlewares.offsite] DEBUG: Filtered offsite request to 'www.baidu.com': <GET https://www.baidu.com/>
2018-10-23 18:28:37 [scrapy.core.scraper] DEBUG: Scraped from <200 http://httpbin.org/get>
{'item': 1}
2018-10-23 18:28:38 [scrapy.extensions.logstats] INFO: Crawled 2 pages (at 60 pages/min), scraped 1 items (at 60 items/min)
2018-10-23 18:28:39 [scrapy.extensions.logstats] INFO: Crawled 2 pages (at 0 pages/min), scraped 1 items (at 0 items/min)
2018-10-23 18:28:39 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://httpbin.org/headers> (referer: None)
2018-10-23 18:28:39 [scrapy.core.scraper] DEBUG: Scraped from <200 http://httpbin.org/headers>
{'item': 2}
2018-10-23 18:28:40 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 60 pages/min), scraped 2 items (at 60 items/min)
2018-10-23 18:28:41 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:28:42 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:28:43 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:28:44 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:28:45 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:28:46 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:28:47 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:28:48 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:28:49 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:28:50 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:28:51 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:28:52 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:28:53 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:28:54 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:28:55 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:28:56 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:28:57 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:28:58 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:28:58 [scrapy.downloadermiddlewares.retry] DEBUG: Retrying <GET https://google.com/> (failed 1 times): TCP connection timed out: 10060: 由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败。.
2018-10-23 18:28:59 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:00 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:01 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:02 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:03 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:04 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:05 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:06 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:07 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:08 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:09 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:10 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:11 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:12 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:13 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:14 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:15 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:16 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:17 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:18 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:19 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:19 [scrapy.downloadermiddlewares.retry] DEBUG: Retrying <GET https://google.com/> (failed 2 times): TCP connection timed out: 10060: 由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败。.
2018-10-23 18:29:20 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:21 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:22 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:23 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:24 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:25 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:26 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:27 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:28 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:29 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:30 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:31 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:32 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:33 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:34 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:35 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:36 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:37 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:38 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:39 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:40 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:40 [scrapy.downloadermiddlewares.retry] DEBUG: Gave up retrying <GET https://google.com/> (failed 3 times): TCP connection timed out: 10060: 由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败。.
2018-10-23 18:29:41 [scrapy.core.scraper] ERROR: Error downloading <GET https://google.com/>
Traceback (most recent call last):
  File "e:/programdata/anaconda3/envs/py3/lib/site-packages/twisted/internet/defer.py", line 1384, in _inlineCallbacks
    result = result.throwExceptionIntoGenerator(g)
  File "e:/programdata/anaconda3/envs/py3/lib/site-packages/twisted/python/failure.py", line 393, in throwExceptionIntoGenerator
    return g.throw(self.type, self.value, self.tb)
  File "e:/programdata/anaconda3/envs/py3/lib/site-packages/scrapy/core/downloader/middleware.py", line 43, in process_request
    defer.returnValue((yield download_func(request=request,spider=spider)))
twisted.internet.error.TCPTimedOutError: TCP connection timed out: 10060: 由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败。.
2018-10-23 18:29:41 [scrapy.extensions.logstats] INFO: Crawled 3 pages (at 0 pages/min), scraped 2 items (at 0 items/min)
2018-10-23 18:29:41 [scrapy.core.engine] INFO: Closing spider (finished)
2018-10-23 18:29:41 [scrapy.extensions.feedexport] INFO: Stored jsonlines feed (2 items) in: file:///C:/Users/win7/items/demo/test/2018-10-23_182826.jl
"""

END = u"""2018-10-23 18:29:41 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
{'downloader/exception_count': 3,
 'downloader/exception_type_count/twisted.internet.error.TCPTimedOutError': 3,
 b'downloader/request_bytes': 13,
 u'downloader/request_count': 7,
 'downloader/request_method_count/GET': 7,
 'downloader/response_bytes': 1669,
 'downloader/response_count': 4,
 'downloader/response_status_count/200': 2,
 'downloader/response_status_count/302': 1,
 'downloader/response_status_count/404': 1,
 'dupefilter/filtered': 1,
 'finish_reason': 'finished',
 'finish_time': datetime.datetime(2018, 10, 23, 10, 29, 41, 174719),
 'httperror/response_ignored_count': 1,
 'httperror/response_ignored_status_count/404': 1,
 'item_scraped_count': 2,
 'log_count/CRITICAL': 5,
 'log_count/DEBUG': 14,
 'log_count/ERROR': 5,
 'log_count/INFO': 75,
 'log_count/WARNING': 3,
 'offsite/domains': 1,
 'offsite/filtered': 1,
 'request_depth_max': 1,
 'response_received_count': 3,
 'retry/count': 2,
 'retry/max_reached': 1,
 'retry/reason_count/twisted.internet.error.TCPTimedOutError': 2,
 'scheduler/dequeued': 7,
 'scheduler/dequeued/memory': 7,
 'scheduler/enqueued': 7,
 'scheduler/enqueued/memory': 7,
 'start_time': datetime.datetime(2018, 10, 23, 10, 28, 35, 70938)}
2018-10-23 18:29:42 [scrapy.core.engine] INFO: Spider closed (finished)"""
