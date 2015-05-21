# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CLIPS subinterface validator
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from clipsinterface import CLIPSInterfaceValidator


class CLIPSSubInterfaceValidator(CLIPSInterfaceValidator):
    SCOPE = CLIPSInterfaceValidator.SUBINTERFACE
