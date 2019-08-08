# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Vendor: IRE-Polus
# OS:     Taros
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "IRE-Polus.Taros"
    matchers = {"is_BS": {"platform": {"$regex": "BS"}}, "is_EAU": {"platform": {"$regex": "EAU"}}}
