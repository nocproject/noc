# ----------------------------------------------------------------------
# GridVCS test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.comp import smart_text
from noc.core.gridvcs.base import GridVCS


SRC_F0 = """interface Gi0/1
    description test
"""

DELTA_F0 = b"""interface Gi1/0/1
    description Changed
"""

RESULT_F0 = smart_text(DELTA_F0)


SRC_b1 = """interface Gi0/1
    description 1st

interface Gi0/2
    description 2nd
"""

DELTA_b1 = (
    b"\x00\x00\x00\x10\x00\x00\x00$\x00\x00\x00\x1e    description 1st interface\n"
    b"\x00\x00\x005\x00\x00\x00I\x00\x00\x00\x1b    description 2nd uplink\n"
)

RESULT_b1 = """interface Gi0/1
    description 1st interface

interface Gi0/2
    description 2nd uplink
"""

SRC_B2 = """interface Gi0/1
    description 1st

interface Gi0/2
    description 2nd
"""

DELTA_B2 = (
    b"BSDIFF40;\x00\x00\x00\x00\x00\x00\x00'\x00\x00\x00\x00\x00\x00\x00Z"
    b"\x00\x00\x00\x00\x00\x00\x00BZh91AY&SY^P%R\x00\x00\x14p@xh\x00\x10\n\x00"
    b"@\x00 \x00!\x8adm5\x08\x06\x9ahck[\xf1\x044B\x9c\x12\x92\x9f\x17rE8P"
    b"\x90^P%RBZh91AY&SY\x1b\xd1\xa7\xd9\x00\x00\x00D\x00@\x00\x00\x02 \x00!"
    b"\x00\x82\x83\x17rE8P\x90\x1b\xd1\xa7\xd9BZh91AY&SYSjp"
    b"\x12\x00\x00\x00\xd1\x80\x00\x10@\x00\x00-B"
    b"\x00 \x00!\x88\xc4\x10\xc0\x8dX\xe5\xbd<]\xc9\x14\xe1BAM\xa9\xc0H"
)

RESULT_B2 = """interface Gi0/1
    description 1st interface

interface Gi0/2
    description 2nd uplink
"""


@pytest.mark.parametrize(
    ("dtype", "src", "delta", "result"),
    [
        ("F", SRC_F0, DELTA_F0, RESULT_F0),
        ("b", SRC_b1, DELTA_b1, RESULT_b1),
        ("B", SRC_B2, DELTA_B2, RESULT_B2),
    ],
)
def test_apply_delta(dtype, src, delta, result):
    assert GridVCS.apply_delta(dtype, src, delta) == result


SRC_z0 = b"""interface Gi0/1
    description 1st

interface Gi0/2
    description 2nd
"""

RESULT_z0 = (
    b"x\x9c\xcb\xcc+I-JKLNUp\xcf4\xd07\xe4R\x00\x82\x94\xd4\xe2\xe4\xa2\xcc\x82\x92\xcc\xfc<"
    b"\x05\xc3\xe2\x12.\xaeL\x14EF\x18\x8a\x8c\xf2R\xb8\x00\\\xd2\x16\xfa"
)


@pytest.mark.parametrize(("ctype", "src", "result"), [("z", SRC_z0, RESULT_z0)])
def test_compress(ctype, src, result):
    assert GridVCS.compress(src, method=ctype) == result


@pytest.mark.parametrize(("ctype", "src", "result"), [("z", SRC_z0, RESULT_z0)])
def test_decompress(ctype, src, result):
    assert GridVCS.decompress(result, method=ctype) == src
