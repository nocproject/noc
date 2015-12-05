# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vendor: Sencore
## OS:     Probe
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
__author__ = 'FeNikS'
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import HTTP

class Profile(noc.sa.profiles.Profile):
    name = "Sencore.Probe"
    supported_schemes = [HTTP]