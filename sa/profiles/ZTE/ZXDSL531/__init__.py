# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: ZTE
# OS:     ZXDSL531
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
<<<<<<< HEAD
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "ZTE.ZXDSL531"
    pattern_username = "Login name:"
=======
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, HTTP


class Profile(noc.sa.profiles.Profile):
    name = "ZTE.ZXDSL531"
    supported_schemes = [TELNET, HTTP]
    pattern_username = "Login name:"
    pattern_password = "Password:"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_prompt = "^>"
    config_volatile = ["<entry1 sessionID=.+?/>"]
