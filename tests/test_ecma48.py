# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# noc.core.ecma48 unittests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.ecma48 import c, strip_control_sequences


def test_c():
    assert c(0, 0) == 0
    assert c(1, 11) == 27
    assert c(15, 15) == 255


def test_strip_normal():
    """
    Normal text leaved untouched
    :return:
    """
    assert strip_control_sequences("Lorem Ipsum") == "Lorem Ipsum"


def test_control_survive():
    """
    CR,LF and ESC survive from C0 set
    :return:
    """
    assert strip_control_sequences("".join([chr(i) for i in range(32)])) == "\t\n\r"


def test_C1_stripped():
    """
    C1 set stripped (ESC+[ survive)
    :return:
    """
    assert strip_control_sequences("".join(["\x1b" + chr(i) for i in range(64, 96)])) == "\x1b["


def test_incomplete_C1():
    """
    Incomplete C1 passed
    """
    assert strip_control_sequences("\x1b") == "\x1b"


def test_CSI():
    # CSI without P and I stripped
    assert strip_control_sequences("\x1b[@\x1b[a\x1b[~") == ""
    # CSI with I stripped
    assert strip_control_sequences("\x1b[ @\x1b[/~") == ""
    # CSI with P and I stripped
    assert strip_control_sequences("\x1b[0 @\x1b[0;7/~") == ""
    # Cleaned stream
    assert strip_control_sequences("L\x1b[@or\x1b[/~em\x1b[0 @ Ips\x1b[0;7/~um\x07") == "Lorem Ipsum"


def test_incomplete_CSI():
    """
    Incomplete CSI passed
    :return:
    """
    assert strip_control_sequences("\x1b[") == "\x1b["


def test_backspace():
    # Single backspace
    assert strip_control_sequences("123\x084") == "124"
    # Triple backspace
    assert strip_control_sequences("123\x08\x08\x084") == "4"
    # Backspaces followed with spaces
    assert strip_control_sequences("\x08 \x08\x08 \x08\x08 \x08\x08 test") == " test"


def test_ascii_mess():
    """
    ASCII mess
    :return:
    """
    assert strip_control_sequences(
        "\x1b[2J\x1b[?7l\x1b[3;23r\x1b[?6l\x1b[24;27H\x1b[?25h\x1b[24;27H"
        "\x1b[?6l\x1b[1;24r\x1b[?7l\x1b[2J\x1b[24;27H\x1b[1;24r\x1b[24;27H"
        "\x1b[2J\x1b[?7l\x1b[1;24r\x1b[?6l\x1b[24;1H\x1b[1;24r\x1b[24;1H"
        "\x1b[24;1H\x1b[2K\x1b[24;1H\x1b[?25h\x1b[24;1H\x1b[24;1Hswitch# "
        "\x1b[24;1H\x1b[24;13H\x1b[24;1H\x1b[?25h\x1b[24;13H"
    ) == "switch# "
