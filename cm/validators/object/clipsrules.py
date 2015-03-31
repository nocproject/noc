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
from noc.cm.validators.clips import CLIPSValidator

logger = logging.getLogger(__name__)


class CLIPSRulesValidator(CLIPSValidator):
    TITLE = "Object CLIPS Rules"
    DESCRIPTION = """
        Apply one or more CLIPS rules at object level
    """
    CONFIG_FORM = [
        {
            "name": "rule",
            "xtype": "textarea",
            "fieldLabel": "CLIPS Rules",
            "allowBlank": False,
            "grow": True
        }
    ]

    rx_def = re.compile(r"(\(\s*defrule\s+)", re.MULTILINE)

    def prepare(self, rule, **kwargs):
        p = self.rx_def.split(rule)[1:]
        if not p:
            logger.info("No rules to install")
        for rule in [x + y for x, y in zip(p[::2], p[1::2])]:
            self.add_rule(rule)
