# ----------------------------------------------------------------------
# MsgStream client tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.msgstream.queuebuffer import QBuffer


@pytest.mark.parametrize(
    ("input", "output", "size"),
    [
        ([b"abc", b"def", b"ghi", b"klm"], [b"abc", b"def", b"ghi", b"klm"], 4),
        ([b"abc", b"def", b"ghi", b"klm"], [b"abc\ndef", b"ghi\nklm"], 7),
        ([b"abc", b"def", b"ghi", b"klm"], [b"abc\ndef\nghi", b"klm"], 11),
    ],
)
def test_qbuffer(input, output, size):
    q = QBuffer(max_size=size)
    assert list(q._iter_chunks(input, size)) == output
