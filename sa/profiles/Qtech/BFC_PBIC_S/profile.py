# ---------------------------------------------------------------------
# Vendor: Qtech
# OS:     BFC_PBIC_S
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
    name = "Qtech.BFC_PBIC_S"
    # to one SNMP GET request
    snmp_metrics_get_chunk = 1
    # Timeout for snmp GET request
    snmp_metrics_get_timeout = 5

    snmp_response_parser = parse_get_response_strict

    rx_sensor_name = re.compile(r"^\d+$")
    rx_discrete_name = re.compile(r"^\d+/\d+$")

    PORT_TYPE = {
        0: "Дискретный вход",
        1: "Вход по напряжению",
        2: "Вход счетчика импульсов",
        3: "Вход датчика вибрации/удара",
        4: "Вход по сопротивлению",
        9: "Вход сигнала ИБП (Батарея разряжена)",
        10: "Вход сигнала ИБП (Питание от сети)",
    }

    SENSOR_NAME = {
        0: "discrete input",
        1: "load",
        2: "pulse",
        3: "vibration/shock",
        4: "resistance",
        9: "battery",
        10: "ups",
        21: "temperature",
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
        elif is_int(s):
            return self.SENSOR_NAME.get(int(s))
        return s
