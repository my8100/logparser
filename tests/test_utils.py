# coding: utf-8
import os

from logparser.run import STAR
from logparser.utils import check_update


def test_run_py():
    assert STAR  # Test importing of logparser/logparser/run.py


def test_check_update():
    js = check_update(timeout=60)
    assert 'latest_version' in js and 'info' in js


def test_main_pid_exit(psr):
    psr(main_pid=os.getpid())
