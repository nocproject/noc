# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# pyParsing tokens
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
=======
##----------------------------------------------------------------------
## pyParsing tokens
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from pyparsing import (alphanums, Combine, Group, LineEnd, nums, Suppress, Word,
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
# Sequence of letters and numbers
ALPHANUMS = Word(alphanums)
# Number from 0 to 255
OCTET = Word(nums, max=3)
# IPv4 address
IPv4_ADDRESS = Combine(OCTET + "." + OCTET + "." + OCTET + "." + OCTET)
# RD
RD = Combine(Word(nums) + Word(":") + Word(nums))

