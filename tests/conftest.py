# coding: utf8
import os
from shutil import rmtree
import zipfile

import pytest

from logparser.logparser import LogParser
from tests.demo_log import FRONT, END
from tests.utils import cst, SETTINGS


"""
from tests.utils import settings  # settings = dict(SETTINGS) shared between test functions
@pytest.fixture
def parser():
    print('parser fixture')
    print(settings)

    if os.path.isdir(cst.LOGS_PATH):
        rmtree(cst.LOGS_PATH, ignore_errors=True)
    with zipfile.ZipFile(cst.LOGS_ZIP_PATH, 'r') as f:
        f.extractall(cst.CWD)

    parser = LogParser(**settings)
    yield parser

def test_default_settings(parser):
    parser.main()
"""


# https://stackoverflow.com/questions/18011902/py-test-pass-a-parameter-to-a-fixture-function
@pytest.fixture
def psr():
    def new_a_parser(execute_main=True, reset_logs=True, **kwargs):
        if reset_logs:
            if os.path.isdir(cst.LOGS_PATH):
                rmtree(cst.LOGS_PATH, ignore_errors=True)
            import time
            time.sleep(1)
            with zipfile.ZipFile(cst.LOGS_ZIP_PATH, 'r') as f:
                f.extractall(cst.CWD)
            cst.write_text(cst.LOG_PATH, FRONT + END)
            cst.write_text(cst.TXT_PATH, FRONT + END)

        settings = dict(SETTINGS)
        if kwargs:
            settings.update(kwargs)
        print(settings)

        parser = LogParser(**settings)
        if execute_main:
            parser.main()
        return parser

    yield new_a_parser
