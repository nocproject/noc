# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Test python module loading
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import subprocess
import os
import ast
# Third-party modules
import pytest
import cachetools


@cachetools.cached(cache={})
def get_files():
    try:
        data = subprocess.check_output(["git", "ls-tree", "HEAD", "-r", "--name-only"])
        return data.splitlines()
    except (OSError, subprocess.CalledProcessError):
        # No git, emulate
        data = subprocess.check_output(["find", ".", "-type", "f", "-print"])
        return [p[:2] for p in data.splitlines()]


@cachetools.cached(cache={})
def get_py_modules_list():
    result = []
    for path in get_files():
        if path.startswith(".") or not path.endswith(".py"):
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


@pytest.mark.parametrize("module", get_py_modules_list())
def test_import(module):
    m = __import__(module, {}, {}, "*")
    assert m


@pytest.mark.parametrize("module", get_py_modules_list())
def test_module_empty_docstrings(module):
    m = __import__(module, {}, {}, "*")
    if m.__doc__ is not None and not m.__doc__.strip():
        # assert m.__doc__.strip(), "Module-level docstring must not be empty"
        pytest.xfail("Module-level docstring must not be empty")


@pytest.mark.parametrize("path", [f for f in get_files() if f.endswith("__init__.py")])
def test_init(path):
    with open(path) as f:
        data = f.read()
    n = compile(data, path, "exec", ast.PyCF_ONLY_AST)
    assert bool(n.body) or not bool(data), "__init__.py must be empty"
