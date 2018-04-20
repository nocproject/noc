# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Vendor: Alcatel
# OS:     OS62xx
# Compatible: OS LS6224
# ----------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Alcatel.OS62xx"
=======
##----------------------------------------------------------------------
## Vendor: Alcatel
## OS:     OS62xx
## Compatible: OS LS6224
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "Alcatel.OS62xx"
    supported_schemes = [TELNET, SSH]
    pattern_username = "User Name:"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_more = "^More: .*?$"
    command_more = " "
    command_disable_pager = "terminal datadump"
