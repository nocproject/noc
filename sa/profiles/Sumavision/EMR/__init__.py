# !/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'feniks'

#NOC modules
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import SSH


class Profile(noc.sa.profiles.Profile):
    name = "SUMAVISION.EMR"
    supported_schemes = [SSH]