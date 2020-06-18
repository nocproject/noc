# ----------------------------------------------------------------------
# CodeMorph test
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
import pytest

# NOC modules
from noc.core.codemorph import CodeMorpher


SRC_IF1 = """print(1)
print(2)
# if True {
print(3)
if 1 > 2:
    print(4)
# }
print(5)
"""

EXP_SRC_IF1 = """print(1)
print(2)
print(3)
if 1 > 2:
    print(4)
print(5)
"""

SRC_IF2 = """print(1)
print(2)
# if False {
print(3)
if 1 > 2:
    print(4)
# }
print(5)
"""

EXP_SRC_IF2 = """print(1)
print(2)
print(5)
"""

SRC_IF3 = """print(1)
print(2)
# if True {
if True:
    print(3)
    if 1 > 2:
        print(4)
# }
print(5)
"""

EXP_SRC_IF3 = """print(1)
print(2)
print(3)
if 1 > 2:
    print(4)
print(5)
"""

SRC_IF4 = """print(1)
# if self.default is not None {
if value is None and self.default is not None:
    return self.default
# }
print(2)
"""


class DefaultSelf(object):
    default = 1


class NoDefaultSelf(object):
    default = None


EXP_SRC_IF4_DEFAULT = """print(1)
if value is None:
    return self.default
print(2)
"""

EXP_SRC_IF4_NODEFAULT = """print(1)
print(2)
"""

SRC_CLEAN = """    def clean(self, value):
        # if self.default is not None {
        if value is None and self.default is not None:
            return self.default
        # }
        if not isinstance(value, str):
            try:
                value = str(value)
            except Exception:
                self.raise_error(value)
        # if self.aliases {
        if self.aliases:
            value = self.aliases.get(value, value)
        # }
        # if self.choices {
        if self.choices and value not in self.choices:
            self.raise_error(value)
        # }
        return value
"""


class SPMinimal(object):
    default = None
    aliases = None
    choices = None


EXP_SPMINIMAL = """    def clean(self, value):
        if not isinstance(value, str):
            try:
                value = str(value)
            except Exception:
                self.raise_error(value)

        return value
"""


class SPDefault(object):
    default = "x"
    aliases = None
    choices = None


EXP_SPDEFAULT = """    def clean(self, value):
        if value is None:
            return self.default
        if not isinstance(value, str):
            try:
                value = str(value)
            except Exception:
                self.raise_error(value)

        return value
"""


@pytest.mark.parametrize(
    "src,ctx,expected",
    [
        (SRC_IF1, {}, EXP_SRC_IF1),
        (SRC_IF2, {}, EXP_SRC_IF2),
        (SRC_IF3, {}, EXP_SRC_IF3),
        (SRC_IF4, {"self": DefaultSelf()}, EXP_SRC_IF4_DEFAULT),
        (SRC_IF4, {"self": NoDefaultSelf()}, EXP_SRC_IF4_NODEFAULT),
        (SRC_CLEAN, {"self": SPMinimal()}, EXP_SPMINIMAL),
        (SRC_CLEAN, {"self": SPDefault}, EXP_SPDEFAULT),
    ],
)
def test_codemorpher(src, ctx, expected):
    cm = CodeMorpher()
    assert cm.code_morph_text(src, ctx) == expected


SRC_DEDENT1 = """print(1)
print(2)
"""

EXP_DEDENT1 = """print(1)
print(2)
"""

SRC_DEDENT2 = """    print(1)
    print(2)
print(3)
print(4)
"""

EXP_DEDENT2 = """print(1)
print(2)
print(3)
print(4)
"""


@pytest.mark.parametrize("src,expected", [(SRC_DEDENT1, EXP_DEDENT1), (SRC_DEDENT2, EXP_DEDENT2)])
def test_dedent(src, expected):
    cm = CodeMorpher()
    assert cm.dedent(src) == expected
