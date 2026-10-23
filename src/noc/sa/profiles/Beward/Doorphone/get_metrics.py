# ---------------------------------------------------------------------
# Beward.Doorphone.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics


class Script(GetMetricsScript):
    name = "Beward.Doorphone.get_metrics"

    @metrics(["Beward | Doorphone | PhoneVolume"], volatile=False, access="S")  # SNMP version
    def get_phone_volume(self, metrics):
        phone_volume = self.snmp.get("1.3.6.1.4.1.44490.1.5.3.0")

        if phone_volume:
            self.set_metric(
                id=("Beward | Doorphone | PhoneVolume", None),
                metric="Beward | Doorphone | PhoneVolume",
                value=phone_volume,
                units="1",
            )

    @metrics(
        [
            "Interface | Speed",
            "Interface | Packets | In",
            "Interface | Packets | Out",
            "Interface | Errors | Out",
            "Interface | Octets | In",
            "Interface | Octets | Out",
        ],
        volatile=False,
        access="S",
    )  # SNMP version
    def get_interface_metrics(self, metrics):
        iface_name = self.snmp.get("1.3.6.1.2.1.31.1.1.1.1.2")
        speed = self.snmp.get("1.3.6.1.2.1.2.2.1.5.2")
        packets_in = self.snmp.get("1.0.8802.1.1.2.1.2.6.1.2.2")
        packets_out = self.snmp.get("1.0.8802.1.1.2.1.2.7.1.4.2")
        errors_out = self.snmp.get("1.0.8802.1.1.2.1.2.7.1.3.2")
        octets_in = self.snmp.get("1.3.6.1.2.1.31.1.1.1.6.2")
        octets_out = self.snmp.get("1.3.6.1.2.1.31.1.1.1.10.2")

        if speed:
            self.set_metric(
                id=("Interface | Speed", None),
                labels=[f"noc::interface::{iface_name}"],
                metric="Interface | Speed",
                value=int(speed),
                units="bit/s",
            )
        if packets_in:
            self.set_metric(
                id=("Interface | Packets | In", None),
                labels=[f"noc::interface::{iface_name}"],
                value=packets_in,
                units="pkt",
            )
        if packets_out:
            self.set_metric(
                id=("Interface | Packets | Out", None),
                labels=[f"noc::interface::{iface_name}"],
                value=packets_out,
                units="pkt",
            )
        if errors_out:
            self.set_metric(
                id=("Interface | Errors | Out", None),
                labels=[f"noc::interface::{iface_name}"],
                value=errors_out,
                units="pkt",
            )
        if octets_in:
            self.set_metric(
                id=("Interface | Octets | In", None),
                labels=[f"noc::interface::{iface_name}"],
                value=octets_in,
                units="byte",
            )
        if octets_out:
            self.set_metric(
                id=("Interface | Octets | Out", None),
                labels=[f"noc::interface::{iface_name}"],
                value=octets_out,
                units="byte",
            )

    @metrics(["SIP | Status"], volatile=False, access="S")  # SNMP version
    def get_sip_status(self, metrics):
        """
        Get SIP Status on device:
        result:
        1 - active,
        2 - not active,
        3 - broken.
        """
        sip_status = self.snmp.get("1.3.6.1.4.1.44490.1.5.1.0")
        if sip_status:
            self.set_metric(
                id=("SIP | Status", None), metric="SIP | Status", value=sip_status, units="1"
            )
