# ----------------------------------------------------------------------
# NSN.TIMOS.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics


class Script(GetMetricsScript):
    name = "NSN.TIMOS.get_metrics"

    @metrics(
        ["Subscribers | Summary"],
        has_capability="BRAS | PPPoE",
        volatile=False, access="S",
    )
    def get_subscribers_metrics_snmp(self, metrics):
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.6527.3.1.2.33.1.106.1.2.1", bulk=False):
            oid2 = oid.split("1.3.6.1.4.1.6527.3.1.2.33.1.106.1.2.1.")
            slot = "slot "
            slot += str(oid2[1])
            if int(v) > 0:
                self.set_metric(
                    id=("Subscribers | Summary", None),
                    labels=("noc::chassis::0", f"noc::slot::{slot}"),
                    value=int(v),
                    multi=True,
                )
        names = {x: y for y, x in self.scripts.get_ifindexes().items()}
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.6527.3.1.2.33.1.104.1.60.1", bulk=False):
            oid2 = oid.split("1.3.6.1.4.1.6527.3.1.2.33.1.104.1.60.1.")
            port = names[int(oid2[1])]
            if int(v) > 0:
                self.set_metric(
                    id=("Subscribers | Summary", None),
                    labels=("noc::chassis::0", f"noc::interface::{str(port)}"),
                    value=int(v),
                    multi=True,
                )
        metric = self.snmp.get("1.3.6.1.4.1.6527.3.1.2.33.5.9.1.2.1")
        if metric:
            self.set_metric(
                id=("Subscribers | Summary", None),
                labels=("noc::chassis::0",),
                value=int(metric),
                multi=True,
            )

    @metrics(
        [
            "Object | QoS | Dynamic Queue | Usage",
            "Object | QoS | Dynamic Queue | Count",
            "Object | QoS | Dynamic Policy | Usage",
            "Object | QoS | Dynamic Policy | Count",
        ],
        # has_capability="BRAS | PPPoE",
        volatile=False,
        access="S",
    )
    def get_qos_queue_metrics_snmp(self, metrics):
        # QoS dynamic queue limit
        qos_queue_limit = {}
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.6527.3.1.2.2.3.46.1.25"):
            _, key = oid.split(".25.")
            qos_queue_limit[tuple(key)] = float(v)
        # QoS dynamic queue value
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.6527.3.1.2.2.3.46.1.26"):
            _, key = oid.split(".26.")
            self.set_metric(
                id=("Object | QoS | Dynamic Queue | Count", None),
                labels=[f"noc::slot::{key}"],
                value=float(v),
                multi=True,
            )
            self.set_metric(
                id=("Object | QoS | Dynamic Queue | Usage", None),
                labels=[f"noc::slot::{key}"],
                value=round(float(v) * 100.0 / qos_queue_limit[tuple(key)]),
                multi=True,
            )

        # QoS dynamic policer limit
        qos_policer_limit = {}
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.6527.3.1.2.2.3.46.1.29"):
            _, key = oid.split(".29.")
            qos_policer_limit[tuple(key)] = float(v)
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.6527.3.1.2.2.3.46.1.30"):
            _, key = oid.split(".30.")
            self.set_metric(
                id=("Object | QoS | Dynamic Policy | Count", None),
                labels=[f"noc::slot::{key}"],
                value=float(v),
                multi=True,
            )
            self.set_metric(
                id=("Object | QoS | Dynamic Policy | Usage", None),
                labels=[f"noc::slot::{key}"],
                value=round(float(v) * 100.0 / qos_policer_limit[tuple(key)]),
                multi=True,
            )

    @metrics(
        ["Environment | Temperature"],
        # has_capability="BRAS | PPPoE",
        volatile=False,
        access="S",
    )
    def get_temperature_metrics_snmp(self, metrics):
        temperature = {}
        # Name	 tmnxHwTemperature
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.6527.3.1.2.2.1.8.1.18.1", cached=True):
            _, key = oid.split(".8.1.18.1.")
            temperature[tuple(key)] = int(v)
        # Name	 tmnxHwName
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.6527.3.1.2.2.1.8.1.8.1", cached=True):
            _, key = oid.split(".8.1.8.1.")
            if temperature[tuple(key)] > -128:
                self.set_metric(
                    id=("Environment | Temperature", None),
                    labels=[
                        "noc::chassis::0",
                        "noc::slot::0",
                        f"noc::sensor::Temperature Sensor ({v})",
                    ],
                    value=temperature[tuple(key)],
                    multi=True,
                )

    @metrics(
        ["DHCP | Pool | Used"],
        has_capability="BRAS | PPPoE",
        volatile=False, access="S",
    )
    def get_dhcp_used_metrics_snmp(self, metrics):
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.6527.3.1.2.47.1.17.1.21"):
            _, key = oid.split(".21.1.")
            key = key.split(".")
            pool = "".join([chr(int(c)) for c in key[1:-7]])
            pool = pool.replace("\t", ":")
            pool = pool.replace("\n", ":")
            pool_ip = ".".join([c for c in key[-5:-1]])
            pool_mask = key[-1:][0]
            self.set_metric(
                id=("DHCP | Pool | Used", None),
                labels=[f"noc::dhcp::pool::{pool}", f"noc::dhcp::net::{pool_ip}/{pool_mask}"],
                value=v,
                multi=True,
            )

    @metrics(
        ["Environment | Sensor Status"],
        volatile=False,
        access="S",
    )
    def get_sensor_status(self, metrics):
        v = self.snmp.get("1.3.6.1.4.1.6527.3.1.2.2.1.24.1.1.2.3.1.1", cached=True)
        if v:
            if v == 3:
                v = 1
            else:
                v = 0
            self.set_metric(
                id=("Environment | Sensor Status", None),
                labels=["noc::sensor::State Fan"],
                value=v,
                multi=True,
            )
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.6527.3.1.2.2.1.24.2.1.6"):
            if v == 3:
                v = 1
            else:
                v = 0
            self.set_metric(
                id=("Environment | Sensor Status", None),
                labels=[f"noc::sensor::State PSU {oid[-1]}"],
                value=v,
                multi=True,
            )

    @metrics(
        [
            "RADIUS | Requests",
            "RADIUS | Responses",
        ],
        # has_capability="BRAS | PPPoE",
        volatile=False,
        access="S",
    )
    def get_radius_metrics_snmp(self, metrics):
        # tmnxRadSrvPlcyStatsTxRequests
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.6527.3.1.2.79.1.2.3.1.1"):
            _, key = oid.split(".79.1.2.3.1.1.")
            key = key.split(".")
            name_radius = "".join([chr(int(c)) for c in key])
            self.set_metric(
                id=("RADIUS | Requests", None),
                labels=[f"noc::radius::requests::{name_radius}"],
                value=v,
                multi=True,
            )
        # tmnxRadSrvPlcyStatsRxResponses
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.6527.3.1.2.79.1.2.3.1.2"):
            _, key = oid.split(".79.1.2.3.1.2.")
            key = key.split(".")
            name_radius = "".join([chr(int(c)) for c in key])
            self.set_metric(
                id=("RADIUS | Responses", None),
                labels=[f"noc::radius::responses::{name_radius}"],
                value=v,
                multi=True,
            )
