# ----------------------------------------------------------------------
# profile errors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.error import NOCError, ERR_SA_NO_PROFILE


class NoSAProfileError(NOCError):
    default_msg = "SA profile not found"
    default_code = ERR_SA_NO_PROFILE
