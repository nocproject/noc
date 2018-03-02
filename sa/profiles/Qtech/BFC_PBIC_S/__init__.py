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
# Python module
import re
# NOC module
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "Qtech.BFC_PBIC_S"
    # to one SNMP GET request
    snmp_metrics_get_chunk = 3
    # Timeout for snmp GET request
    snmp_metrics_get_timeout = 5

    rx_interface_name = re.compile(r"^\d+$")

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("1")
        'DryContact 1'
        """
        match = self.rx_interface_name.match(s)
        if not match:
            return s
        else:
            return "DryContact %s" % s
