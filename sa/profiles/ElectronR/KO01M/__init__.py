# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: ElectronR
# OS:     KO01M
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
'''
'''
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "ElectronR.KO01M"
    # to one SNMP GET request
    snmp_metrics_get_chunk = 4
    # Timeout for snmp GET request
    snmp_metrics_get_timeout = 3
