# ----------------------------------------------------------------------
# NSN.TIMOS.get_metrics
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, metrics


class Script(GetMetricsScript):
    name = "NSN.TIMOS.get_metrics"

    @metrics(
        ["Subscribers | Summary"],
        has_capability="BRAS | PPPoE",
        volatile=False,
        access="S",
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
                    units="C",
                )

    @metrics(
        ["DHCP | Pool | Leases | Active"],
        has_capability="Network | DHCP",
        volatile=False,
        access="S",
    )
    def get_dhcp_used_metrics_snmp(self, metrics):
        """
        tmnxDhcpSvrSubnetStatsUsed 1.3.6.1.4.1.6527.3.1.2.47.1.17.1.21 - IPV4
        tmnxDhcpSvrSubnetStats6Stable 1.3.6.1.4.1.6527.3.1.2.47.1.24.1.2 - IPV6
        """
        for oid_ in ["1.3.6.1.4.1.6527.3.1.2.47.1.17.1.21", "1.3.6.1.4.1.6527.3.1.2.47.1.24.1.2"]:
            for oid, v in self.snmp.getnext(oid_):
                if not oid.startswith(f"{oid_}.1."):
                    # Example - 1.3.6.1.4.1.6527.3.1.2.47.1.17.1.21.4.
                    continue
                _, key = oid.split(f"{oid_}.1.")
                pool, pool_ip, pool_mask = self.profile.ascii_to_str(key)
                self.set_metric(
                    id=("DHCP | Pool | Leases | Active", None),
                    labels=[
                        f"noc::ippool::name::{pool}",
                        f"noc::ippool::prefix::{pool_ip}/{pool_mask}",
                        "noc::ippool::type::dhcp",
                    ],
                    value=v,
                    multi=True,
                )

    @metrics(
        ["DHCP | Pool | Leases | Free"],
        has_capability="Network | DHCP",
        volatile=False,
        access="S",
    )
    def get_dhcp_free_metrics_snmp(self, metrics):
        """
        tmnxDhcpSvrSubnetStatsFree 1.3.6.1.4.1.6527.3.1.2.47.1.17.1.1  - IPV4
        tmnxDhcpSvrSubnetStats6FreeBlk 1.3.6.1.4.1.6527.3.1.2.47.1.24.1.14  - IPV6
        """
        for oid_ in ["1.3.6.1.4.1.6527.3.1.2.47.1.17.1.1", "1.3.6.1.4.1.6527.3.1.2.47.1.24.1.14"]:
            for oid, v in self.snmp.getnext(oid_):
                if not oid.startswith(f"{oid_}.1."):
                    continue
                _, key = oid.split(f"{oid_}.1.")
                pool, pool_ip, pool_mask = self.profile.ascii_to_str(key)
                self.set_metric(
                    id=("DHCP | Pool | Leases | Free", None),
                    labels=[
                        f"noc::ippool::name::{pool}",
                        f"noc::ippool::prefix::{pool_ip}/{pool_mask}",
                        "noc::ippool::type::dhcp",
                    ],
                    value=v,
                    multi=True,
                )

    @metrics(
        ["DHCP | Pool | Leases | Active | Percent"],
        has_capability="Network | DHCP",
        volatile=False,
        access="S",
    )
    def get_dhcp_active_percent_metrics_snmp(self, metrics):
        """
        tmnxDhcpSvrSubnetStatsUsedPct 1.3.6.1.4.1.6527.3.1.2.47.1.17.1.31  - IPV4
        tmnxDhcpSvrSubnetStats6UsedPct 1.3.6.1.4.1.6527.3.1.2.47.1.24.1.17  - IPV6
        """
        for oid_ in ["1.3.6.1.4.1.6527.3.1.2.47.1.17.1.31", "1.3.6.1.4.1.6527.3.1.2.47.1.24.1.17"]:
            for oid, v in self.snmp.getnext(oid_):
                if not oid.startswith(f"{oid_}.1."):
                    continue
                _, key = oid.split(f"{oid_}.1.")
                pool, pool_ip, pool_mask = self.profile.ascii_to_str(key)
                self.set_metric(
                    id=("DHCP | Pool | Leases | Active | Percent", None),
                    labels=[
                        f"noc::ippool::name::{pool}",
                        f"noc::ippool::prefix::{pool_ip}/{pool_mask}",
                        "noc::ippool::type::dhcp",
                    ],
                    value=v,
                    multi=True,
                    units="%",
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
            "Radius | Policy | Request | Count",
            "Radius | Policy | Request | Delta",
            "Radius | Policy | Response | Delta",
            "Radius | Policy | Response | Count",
        ],
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
                id=("Radius | Policy | Request | Count", None),
                labels=[f"noc::radius::{name_radius}"],
                value=v,
                multi=True,
            )
            self.set_metric(
                id=("Radius | Policy | Request | Delta", None),
                labels=[f"noc::radius::{name_radius}"],
                type="delta",
                value=v,
                multi=True,
            )
        # tmnxRadSrvPlcyStatsRxResponses
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.6527.3.1.2.79.1.2.3.1.2"):
            _, key = oid.split(".79.1.2.3.1.2.")
            key = key.split(".")
            name_radius = "".join([chr(int(c)) for c in key])
            self.set_metric(
                id=("Radius | Policy | Response | Count", None),
                labels=[f"noc::radius::{name_radius}"],
                value=v,
                multi=True,
            )
            self.set_metric(
                id=("Radius | Policy | Response | Delta", None),
                labels=[f"noc::radius::{name_radius}"],
                type="delta",
                value=v,
                multi=True,
            )
