# ----------------------------------------------------------------------
# noc.core.fileutils tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import time
from pathlib import Path

# Third-party modules
import pytest

# NOC modules
from noc.core.fileutils import safe_rewrite, temporary_file, write_tempfile


@pytest.mark.parametrize(
    ("start", "tail", "expected"),
    [
        ("lorem ipsum\n", "dorem sit amet", "lorem ipsum\ndorem sit amet"),
        ("Буря мглою ", "небо кроет", "Буря мглою небо кроет"),
    ],
)
def test_read_write(start: str, tail: str, expected: str) -> None:
    fn = os.path.join("/tmp", f"noc-test-fu-{int(time.time())}")
    safe_rewrite(fn, start)
    with open(fn, "a") as f:
        f.write(tail)
    data = Path(fn).read_text()
    os.unlink(fn)
    assert data == expected


@pytest.mark.parametrize("text", ["Lorem ipsum dorem sit amet", "Буря мглою небо кроет"])
def test_write_tempfile(text: str) -> None:
    fn = write_tempfile(text)
    assert os.path.exists(fn)
    data = Path(fn).read_text()
    os.unlink(fn)
    assert data == text


@pytest.mark.parametrize("text", ["Lorem ipsum dorem sit amet", "Буря мглою небо кроет"])
def test_temporary_file(text: str) -> None:
    with temporary_file(text) as fn:
        assert os.path.exists(fn)
        data = Path(fn).read_text()
    assert not os.path.exists(fn)
    assert data == text
