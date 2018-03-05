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
# Python module
import re
# NOC module
from noc.core.profile.base import BaseProfile


class Profile(BaseProfile):
    name = "ElectronR.KO01M"
    # to one SNMP GET request
    snmp_metrics_get_chunk = 4
    # Timeout for snmp GET request
    snmp_metrics_get_timeout = 3

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
