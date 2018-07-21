# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# noc.core.crypto test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.crypto import gen_salt, md5crypt


def test_salt_length():
    assert len(gen_salt(4)) == 4
    assert len(gen_salt(10)) == 10


def test_md5_crypt():
    assert md5crypt("test", salt="1234") == "$1$1234$InX9CGnHSFgHD3OZHTyt3."
    assert md5crypt("test", salt="1234") == "$1$1234$InX9CGnHSFgHD3OZHTyt3."
    assert md5crypt("test", salt="1234", magic="$5$") == "$5$1234$x29w4cwzSDnesjss/m2O1."
