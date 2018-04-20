# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Hostname *MUST NOT* be empty
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## Hostname *MUST NOT* be empty
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
