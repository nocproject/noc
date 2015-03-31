# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Hostname *MUST* match DB
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import logging
## NOC modules
from noc.cm.validators.base import BaseValidator

logger = logging.getLogger(__name__)


class HostnameMatchRegexpValidator(BaseValidator):
    TITLE = "Hostname *MUST* match regexp"
    DESCRIPTION = """
        Hostname *MUST* match regexp
    """

    CONFIG_FORM = [
        {
            "name": "regexp",
            "xtype": "textfield",
            "fieldLabel": "Hostname REGEXP",
            "allowBlank": False
        }
    ]

    def check(self, regexp, **kwargs):
        # Get system fact
        sf = self.engine.find_one(cls="system")
        if not sf:
            return
        # Check regexp
        try:
            rx = re.compile(regexp)
        except Exception, why:
            self.assert_error(
                "Validator | Internal Error",
                obj=self.rule.name,
                msg=str(why)
            )
            return
        # Check regexp
        if sf.hostname is not None and not rx.search(sf.hostname):
            self.assert_error(
                "System | Hostname Mismatches Regexp",
                msg=regexp
            )
