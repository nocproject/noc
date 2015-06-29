# !/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'boris'
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, HTTP


class Profile(noc.sa.profiles.Profile):
    name = "Tangram.GT21"
    supported_schemes = [TELNET, HTTP]
    pattern_more = "CTRL\+C.+?a All"
    pattern_prompt = r"^>"