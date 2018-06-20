# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Test python module loading
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import subprocess
import os
# Third-party modules
import pytest


def _git_ls():
    try:
        data = subprocess.check_output(["git", "ls-tree", "HEAD", "-r", "--name-only"])
        return data.splitlines()
    except OSError:
        # No git
        return []


def get_py_modules_list():
    result = []
    for path in _git_ls():
        if not path.endswith(".py"):
            continue
        parts = path.split(os.sep)
        if parts[0] == "tests" or path == "setup.py":
            continue
        fn = parts[-1]
        if fn.startswith("."):
            continue
        if fn == "__init__.py":
            # Strip __init__.py
            parts = parts[:-1]
        else:
            # Strip .py
            parts[-1] = fn[:-3]
        result += [".".join(["noc"] + parts)]
    return result


@pytest.fixture(params=get_py_modules_list())
def py_module(request):
    return request.param


def test_py_module_loading(py_module):
    m = __import__(py_module, {}, {}, "*")
    assert m
