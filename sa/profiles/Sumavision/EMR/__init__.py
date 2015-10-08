# !/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'FeNikS'

#NOC modules
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import HTTP


class Profile(noc.sa.profiles.Profile):
    name = "Sumavision.EMR"
    supported_schemes = [HTTP]