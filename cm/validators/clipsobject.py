# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CLIPS interface validator
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from clips import CLIPSValidator


class CLIPSObjectValidator(CLIPSValidator):
    SCOPE = CLIPSValidator.OBJECT
