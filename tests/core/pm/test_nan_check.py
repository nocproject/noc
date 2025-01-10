# ----------------------------------------------------------------------
# CH \\N check
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Tuple

# Third-party modules
import pytest

# NOC modules
from noc.core.pm.utils import is_nan


@pytest.mark.parametrize(
    ("x", "expected"),
    [
        (("0", "1", "2"), False),
        (("\\N", "1", "2"), True),
        (("0", "\\N", "2"), True),
        (("0", "1", "\\N"), True),
        (("\\N", "\\N", "\\N"), True),
    ],
)
def test_is_nan(x: Tuple[str], expected: bool) -> None:
    assert is_nan(*x) == expected
