# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Alentis
## OS:     NetPing
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import HTTP


class Profile(noc.sa.profiles.Profile):
    name = "Alentis.NetPing"
    supported_schemes = [HTTP]
