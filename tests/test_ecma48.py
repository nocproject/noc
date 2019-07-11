# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# noc.core.ecma48 unittests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.ecma48 import c, strip_control_sequences


@pytest.mark.parametrize("config,expected", [([0, 0], 0), ([1, 11], 27), ([15, 15], 255)])
def test_c(config, expected):
    assert c(*config) == expected


@pytest.mark.parametrize("config,expected", [("Lorem Ipsum", "Lorem Ipsum")])
def test_strip_normal(config, expected):
    """
    Normal text leaved untouched
    :return:
    """
    assert strip_control_sequences(config) == expected


@pytest.mark.parametrize("config,expected", [("".join([chr(i) for i in range(32)]), "\t\n\r")])
def test_control_survive(config, expected):
    """
    CR,LF and ESC survive from C0 set
    :return:
    """
    assert strip_control_sequences(config) == expected


@pytest.mark.parametrize(
    "config,expected", [("".join(["\x1b" + chr(i) for i in range(64, 96)]), "\x1b[")]
)
def test_C1_stripped(config, expected):
    """
    C1 set stripped (ESC+[ survive)
    :return:
    """
    assert strip_control_sequences(config) == expected


@pytest.mark.parametrize("config,expected", [("\x1b", "\x1b")])
def test_incomplete_C1(config, expected):
    """
    Incomplete C1 passed
    :return:
    """
    assert strip_control_sequences(config) == expected


@pytest.mark.parametrize(
    "config,expected",
    [
        ("\x1b[@\x1b[a\x1b[~", ""),
        ("\x1b[ @\x1b[/~", ""),
        ("\x1b[0 @\x1b[0;7/~", ""),
        ("L\x1b[@or\x1b[/~em\x1b[0 @ Ips\x1b[0;7/~um\x07", "Lorem Ipsum"),
    ],
)
def test_CSI(config, expected):
    """
    CSI without P and I stripped
    CSI with I stripped
    CSI with P and I stripped
    Cleaned stream
    :return:
    """
    assert strip_control_sequences(config) == expected


@pytest.mark.parametrize("config,expected", [("\x1b[", "\x1b[")])
def test_incomplete_CSI(config, expected):
    """
    Incomplete CSI passed
    :return:
    """
    assert strip_control_sequences(config) == expected


@pytest.mark.parametrize(
    "config,expected",
    [
        ("123\x084", "124"),
        ("123\x08\x08\x084", "4"),
        ("\x08 \x08\x08 \x08\x08 \x08\x08 test", " test"),
    ],
)
def test_backspace(config, expected):
    """
    Single backspace
    Triple backspace
    Backspaces followed with spaces
    :return:
    """
    assert strip_control_sequences(config) == expected


@pytest.mark.parametrize(
    "config,expected",
    [
        (
            "\x1b[2J\x1b[?7l\x1b[3;23r\x1b[?6l\x1b[24;27H\x1b[?25h\x1b[24;27H"
            "\x1b[?6l\x1b[1;24r\x1b[?7l\x1b[2J\x1b[24;27H\x1b[1;24r\x1b[24;27H"
            "\x1b[2J\x1b[?7l\x1b[1;24r\x1b[?6l\x1b[24;1H\x1b[1;24r\x1b[24;1H"
            "\x1b[24;1H\x1b[2K\x1b[24;1H\x1b[?25h\x1b[24;1H\x1b[24;1Hswitch# "
            "\x1b[24;1H\x1b[24;13H\x1b[24;1H\x1b[?25h\x1b[24;13H",
            "switch# ",
        )
    ],
)
def test_ascii_mess(config, expected):
    """
    ASCII mess
    :return:
    """
    assert strip_control_sequences(config) == expected
