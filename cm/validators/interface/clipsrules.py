# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CLIPS rule-based validator
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
import re
## NOC modules
from noc.cm.validators.object.clipsrules import CLIPSRulesValidator

logger = logging.getLogger(__name__)


class InterfaceCLIPSRulesValidator(CLIPSRulesValidator):
    TITLE = "Interface CLIPS Rules"
    DESCRIPTION = """
        Apply one or more CLIPS rules at interface level
    """
    scope = CLIPSRulesValidator.INTERFACE
