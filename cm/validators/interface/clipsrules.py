# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# CLIPS rule-based validator
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging
import re
# NOC modules
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.cm.validators.object.clipsrules import CLIPSRulesValidator

logger = logging.getLogger(__name__)


class InterfaceCLIPSRulesValidator(CLIPSRulesValidator):
    TITLE = "Interface CLIPS Rules"
    DESCRIPTION = """
        Apply one or more CLIPS rules at interface level
    """
    SCOPE = CLIPSRulesValidator.INTERFACE
