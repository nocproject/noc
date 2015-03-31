# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Hostname *MUST* match DB
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## NOC modules
from noc.cm.validators.base import BaseValidator


class MatchObjectNameValidator(BaseValidator):
    TITLE = "Hostname *MUST* match DB"
    DESCRIPTION = """
        Hostname *MUST* match managed object's name
    """

    def check(self, **kwargs):
        # Get system fact
        sf = self.engine.find_one(cls="system")
        if not sf:
            return
        # Exact match
        if sf.hostname == sf.managed_object_name:
            return
        # hostname + domain name match
        if sf.domain_name and "%s.%s" % (sf.hostname, sf.domain_name) == sf.managed_object_name:
            return
        if "." in sf.managed_object_name and not sf.domain_name:
            if sf.managed_object_name.split(".")[0] == sf.hostname:
                return
        #
        self.assert_error(
            "System | Hostname Mismatches DB"
        )