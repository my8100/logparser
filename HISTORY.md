Release History
===============
[0.8.2](https://github.com/my8100/logparser/issues?q=is%3Aclosed+milestone%3A0.8.2) (2019-08-04)
------------------
- New Features
  - Support telneting with auth for Scrapy>=1.5.2, except for Windows and Fedora
- Improvements
  - Add LOG_CATEGORIES_LIMIT option for reducing json file size [(issue #5)](https://github.com/my8100/logparser/issues/5)
- Bug Fixes
  - Fix parsing error due to unicode signs in crawler stats [(issue #2)](https://github.com/my8100/logparser/issues/2)
  - Stats collected via telnet are not being updated periodically [(issue #4)](https://github.com/my8100/logparser/issues/4)
- Others
  - Support continuous integration (CI) on [CircleCI](https://circleci.com/)


0.8.1 (2019-03-12)
------------------
- New Features
  - Support collecting crawler_stats and crawler_engine via telnet if available
  (Note that this feature temporarily only works for [Scrapy 1.5.1](https://doc.scrapy.org/en/latest/news.html#scrapy-1-5-1-2018-07-12) and its earlier version
  since telnet console now requires username and password after [Scrapy 1.5.2](https://doc.scrapy.org/en/latest/news.html#release-1-5-2))
- Improvements
  - Set 'pages' and 'items' of the parsing result to None if not available, instead of 0
  - Change key of the parsing result from 'elapsed' to 'runtime'


0.8.0 (2019-01-20)
------------------
- First release version (compatible with [*ScrapydWeb* v1.1.0](https://github.com/my8100/scrapydweb))
