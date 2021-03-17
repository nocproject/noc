# ----------------------------------------------------------------------
# noc.core.palette tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Set, List
import re

# Third-party modules
import pytest

# NOC modules
from noc.core.palette import (
    ALL_PALETTES,
    COLOR_PALETTES,
    TONE_PALETTES,
    BW,
    AVATAR_COLORS,
    get_avatar_bg_color,
)

ALL_COLORS: Set[str] = set()
for palette in ALL_PALETTES:
    ALL_COLORS.update(palette)

rx_color = re.compile("^#[0-9A-F]{6}$")


@pytest.mark.parametrize("color", ALL_COLORS)
def test_color_item(color: str) -> None:
    assert rx_color.match(color)


@pytest.mark.parametrize("colors", COLOR_PALETTES)
def test_color_palette_size(colors: List[str]) -> None:
    assert len(colors) == 14


@pytest.mark.parametrize("colors", TONE_PALETTES)
def test_tone_palette_size(colors: List[str]) -> None:
    assert len(colors) == 10


def test_bw_palette_size():
    assert len(BW) == 2


def test_get_avatar_bg_color():
    n = len(AVATAR_COLORS)
    # First round
    round1 = [get_avatar_bg_color(i) for i in range(1, n + 1)]
    # Ensure first round effectively covers all colors
    assert len(round1) == n
    assert not (set(AVATAR_COLORS) - set(round1))
    # Second round
    round2 = [get_avatar_bg_color(i) for i in range(n + 1, 2 * n + 1)]
    # First and second round must match
    assert round1 == round2
    # Check repeatability
    round1r = [get_avatar_bg_color(i) for i in range(1, n + 1)]
    assert round1 == round1r
