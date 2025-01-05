# coding: utf-8
import os

from logparser.run import STAR
from logparser.utils import check_update

from tests.utils import cst


def test_run_py():
    assert STAR  # Test importing of logparser/logparser/run.py


def test_check_update():
    js = check_update(timeout=60)
    print(js)
    if js:
        assert 'latest_version' in js and 'info' in js
    elif cst.PY313:
        assert js, js
    else:
        print('Got empty js.')


def test_main_pid_exit(psr):
    psr(main_pid=os.getpid())
