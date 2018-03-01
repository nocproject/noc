# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vendor: Qtech
# OS:     BFC-PBIC-S
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
'''
'''
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Qtech.BFC_PBIC_S"
    # to one SNMP GET request
    snmp_metrics_get_chunk = 3
    # Timeout for snmp GET request
    snmp_metrics_get_timeout = 5

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("1")
        'DryContact 1'
        """
        if "eth0"not in s:
            return "DryContact %s" % s
        else:
            return s
