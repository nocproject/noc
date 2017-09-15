# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Test python module loading
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
# Third-party modules
import pytest


def get_py_modules_list():
    result = []
    for root, dirs, files in os.walk(".", topdown=True):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "lib64"]
        if root == "./lib":
            dirs[:] = [d for d in dirs if d not in ("python", "python2.7")]
        elif root == ".":
            dirs[:] = [d for d in dirs if d not in ("share", "var")]
        for f in files:
            if f.startswith(".") or not f.endswith(".py"):
                continue
            result += [".".join(["noc"] + os.path.join(root, f[:-3]).split(os.sep)[1:])]
    return result


@pytest.fixture(params=get_py_modules_list())
def py_module(request):
    return request.param


def test_py_module_loading(py_module):
    m = __import__(py_module, {}, {}, "*")
    assert m
