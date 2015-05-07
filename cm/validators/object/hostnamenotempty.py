# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Hostname *MUST NOT* be empty
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.cm.validators.base import BaseValidator


class HostnameNotEmptyValidator(BaseValidator):
    TITLE = "Hostname *MUST NOT* be empty"
    DESCRIPTION = """
        Hostname *MUST NOT* be empty
    """

    def check(self, **kwargs):
        # Get system fact
        sf = self.engine.find_one(cls="system")
        if not sf:
            return
        # Exact match
        if not sf.hostname:
            self.assert_error(
                "System | Hostname is Empty"
            )
