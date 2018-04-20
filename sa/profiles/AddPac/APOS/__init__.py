# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Vendor: AddPac
# OS:     APOS
# ----------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "AddPac.APOS"
=======
##----------------------------------------------------------------------
## Vendor: AddPac
## OS:     APOS
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.profiles
from noc.sa.protocols.sae_pb2 import TELNET, SSH


class Profile(noc.sa.profiles.Profile):
    name = "AddPac.APOS"
    supported_schemes = [TELNET, SSH]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    pattern_more = "^-- more --"
    pattern_prompt = r"^\S+?#"
    command_more = " \n"
    command_submit = "\r"
<<<<<<< HEAD
    pattern_unprivileged_prompt = r"^\S+?>"
=======
    pattern_unpriveleged_prompt = r"^\S+?>"
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    command_super = "enable"
