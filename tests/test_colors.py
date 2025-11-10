# ----------------------------------------------------------------------
# noc.core.colors unittests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.colors import get_colors


@pytest.mark.parametrize(
    ("config", "expected"),
    [
        (1, ["#ff0000"]),
        (2, ["#ff0000", "#00ffff"]),
        (3, ["#00ff00", "#ff0000", "#0000ff"]),
        (4, ["#ff0000", "#00ffff", "#7fff00", "#7f00ff"]),
    ],
)
def test_color(config, expected):
    """
    :return:
    """
    assert list(get_colors(config)) == expected
