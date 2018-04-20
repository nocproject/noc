# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: Cisco
# OS:     LinkSys
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Linksys.VoIP"
=======
##----------------------------------------------------------------------
## Vendor: Cisco
## OS:     LinkSys
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import HTTP


class Profile(noc.sa.profiles.Profile):
    name = "Linksys.VoIP"
    supported_schemes = [HTTP]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
