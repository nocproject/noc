# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# MikroTik.SwOS
# Dummb profile to allow managed object creating
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "MikroTik.SwOS"
    snmp_metrics_get_chunk = 5
