# coding: utf-8
import logging

from .__version__ import __version__
from .common import SETTINGS_PY_PATH
# from .logparser import LogParser
from .scrapylogparser import parse


# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
# https://docs.python-guide.org/writing/logging/#logging-in-a-library
logging.getLogger(__name__).addHandler(logging.NullHandler())
