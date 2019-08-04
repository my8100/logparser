# coding: utf-8
from tests.utils import cst


def test_cleantest(psr):
    if cst.ON_WINDOWS and cst.PY2:
        cmd = 'pip install scrapy==1.5.1'
    else:
        cmd = 'pip install --upgrade scrapy'
    cst.sub_process(cmd, block=True)
