# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Test NSQ mpub functions
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.nsq.pub import mpub_encode


@pytest.mark.parametrize(
    "messages,expected",
    [
        # Empty messages
        ([], b""),
        # Single
        (["lorem"], b"\x00\x00\x00\x01\x00\x00\x00\x05lorem"),
        # Multiple
        (
            ["lorem ipsum", "dolor", "sit amet"],
            b"\x00\x00\x00\x03\x00\x00\x00\x0blorem ipsum\x00\x00\x00\x05dolor\x00\x00\x00\x08sit amet",
        ),
        # Mixed
        (
            ["lorem ipsum", 12, {"x": "sit amet"}],
            b'\x00\x00\x00\x03\x00\x00\x00\x0blorem ipsum\x00\x00\x00\x0212\x00\x00\x00\x10{"x":"sit amet"}',
        ),
    ],
)
def test_mpub_encode(messages, expected):
    assert mpub_encode(messages) == expected
