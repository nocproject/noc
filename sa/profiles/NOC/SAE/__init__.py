# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Vendor: NOC
# OS:     SAE
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "NOC.SAE"
=======
##----------------------------------------------------------------------
## Vendor: NOC
## OS:     SAE
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles


class Profile(noc.sa.profiles.Profile):
    name="NOC.SAE"
    supported_schemes = [0]  # Fake telnet

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
