# coding: utf8
import os

from logparser.run import SETTINGS_PY_PATH
from logparser.utils import check_update


def test_settings_py():
    assert os.path.exists(SETTINGS_PY_PATH)  # Test importing of logparser/logparser/run.py


def test_check_update():
    js = check_update()
    assert 'latest_version' in js and 'info' in js


def test_main_pid_exit(psr):
    psr(main_pid=os.getpid())
