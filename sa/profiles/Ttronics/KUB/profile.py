# ---------------------------------------------------------------------
# Vendor: Ttronics
# OS:     KUB
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python module
import re

# NOC module
from noc.core.profile.base import BaseProfile
from noc.core.snmp.get import parse_get_response_strict
from noc.core.validators import is_int


class Profile(BaseProfile):
    name = "Ttronics.KUB"
    # to one SNMP GET request
    snmp_metrics_get_chunk = 1
    # Timeout for snmp GET request
    snmp_metrics_get_timeout = 5

    snmp_response_parser = parse_get_response_strict

    rx_sensor_name = re.compile(r"^\d+$")
    rx_discrete_name = re.compile(r"^\d+/\d+$")

    matchers = {
        "is_femto": {"platform": {"$regex": "FEMTO|Femto"}},
    }

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("1")
        'load'
        >>> Profile().convert_interface_name("0/1")
        'load'
        """
        match = self.rx_discrete_name.findall(s)
        if match:
            return "%s %s" % (self.SENSOR_NAME.get(int(s.split("/")[0])), s.split("/")[1])
        if is_int(s):
            return self.SENSOR_NAME.get(int(s))
        return s
