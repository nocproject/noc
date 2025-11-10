# ----------------------------------------------------------------------
# noc.core.fileutils tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import time
import os

# Third-party modules
import pytest

# NOC modules
from noc.core.fileutils import safe_rewrite, safe_append, read_file, write_tempfile, temporary_file


@pytest.mark.parametrize(
    ("start", "tail", "expected"),
    [
        ("lorem ipsum\n", "dorem sit amet", "lorem ipsum\ndorem sit amet"),
        ("Буря мглою ", "небо кроет", "Буря мглою небо кроет"),
    ],
)
def test_read_write(start, tail, expected):
    fn = os.path.join("/tmp", "noc-test-fu-%d" % time.time())
    safe_rewrite(fn, start)
    safe_append(fn, tail)
    data = read_file(fn)
    os.unlink(fn)
    assert data == expected


@pytest.mark.parametrize("text", ["Lorem ipsum dorem sit amet", "Буря мглою небо кроет"])
def test_write_tempfile(text):
    fn = write_tempfile(text)
    assert os.path.exists(fn)
    data = read_file(fn)
    os.unlink(fn)
    assert data == text


@pytest.mark.parametrize("text", ["Lorem ipsum dorem sit amet", "Буря мглою небо кроет"])
def test_temporary_file(text):
    with temporary_file(text) as fn:
        assert os.path.exists(fn)
        data = read_file(fn)
    assert not os.path.exists(fn)
    assert data == text
