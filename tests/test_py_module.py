# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Test python module loading
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import subprocess
import os
import ast
# Third-party modules
import pytest

_ls_data = None


def _git_ls():
    global _ls_data

    if _ls_data is not None:
        return _ls_data
    try:
        data = subprocess.check_output(["git", "ls-tree", "HEAD", "-r", "--name-only"])
        _ls_data = data.splitlines()
    except OSError:
        # No git
        _ls_data = []
    return _ls_data


def get_py_modules_list():
    result = []
    for path in _git_ls():
        if not path.endswith(".py"):
            continue
        parts = path.split(os.sep)
        if parts[0] == "tests" or path == "setup.py" or "tests" in parts:
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


@pytest.fixture(scope="module", params=get_py_modules_list())
def py_module(request):
    return request.param


def test_import(py_module):
    m = __import__(py_module, {}, {}, "*")
    assert m


@pytest.fixture(scope="module", params=[f for f in _git_ls() if f.endswith("__init__.py")])
def py_init(request):
    return request.param


def test_init(py_init):
    with open(py_init) as f:
        data = f.read()
    n = compile(data, py_init, "exec", ast.PyCF_ONLY_AST)
    assert bool(n.body) or not bool(data), "__init__.py must be empty"
