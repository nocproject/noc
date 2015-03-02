# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pyParsing tokens
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from pyparsing import (Combine, Group, LineEnd, nums, Suppress, Word,
                       restOfLine)

# Match \s+
SPACE = Suppress(Word(" ").leaveWhitespace())
# Match \n\s+
INDENT = Suppress(LineEnd() + SPACE)
# Skip whole line
LINE = Suppress(restOfLine)
#
REST = SPACE + restOfLine

# Sequence of numbers
DIGITS = Word(nums)
# Number from 0 to 255
OCTET = Word(nums, max=3)
# IPv4 address
IPv4_ADDRESS = Combine(OCTET + "." + OCTET + "." + OCTET + "." + OCTET)


