# ---------------------------------------------------------------------
# Vendor: HP
# OS:     OfficeConnect
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.profile.base import BaseProfile
from noc.core.lldp import LLDP_PORT_SUBTYPE_MAC


class Profile(BaseProfile):
    name = "HP.OfficeConnect"

    def convert_interface_name(self, s):
        """
        >>> Profile().convert_interface_name("TRK 1")
        'trk 1'
        >>> Profile().convert_interface_name("1 Gigabit - Level")
        'Gi 12'
        >>> Profile().convert_interface_name("CPU Interface")
        'cpu'
        """
        s = s.lower()
        if s == "CPU Interface":
            return "cpu"
        if s.startswith("trk"):
            return s
        num, *_ = s.split()
        return num

    @classmethod
    def get_interface_type(cls, name: str):
        name = name.lower()
        if name.startswith("trk"):
            return "aggregated"
        if name.startswith("vlan"):
            return "SVI"
        if name.startswith("switch loopback"):
            return "loopback"
        if name.startswith("cpu"):
            return "management"
        return "physical"

    def clean_lldp_neighbor(self, obj, neighbor):
        neighbor = super().clean_lldp_neighbor(obj, neighbor)
        if neighbor["remote_port_subtype"] == LLDP_PORT_SUBTYPE_MAC and neighbor.get(
            "remote_port_description"
        ):
            neighbor["remote_port"] = neighbor["remote_port_description"]
        return neighbor
