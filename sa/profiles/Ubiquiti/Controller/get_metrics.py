# ---------------------------------------------------------------------
# Ubiquiti.Controller.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import time
from typing import List

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, ProfileMetricConfig
from noc.core.models.cfgmetrics import MetricCollectorConfig

NS = 1_000_000_000


class Script(GetMetricsScript):
    """
    WLAN Statistics: /v2/api/site/default/wlan/enriched-configuration
    """
    name = "Ubiquiti.Controller.get_metrics"
    CPE_METRICS_CONFIG = {
        "Radio | TxRetries | Ratio": ProfileMetricConfig(
            metric="Radio | TxRetries | Ratio",
            oid="tx_retries_percentage",
            sla_types=[],
            scale=1,
            units="%",
        ),
        "Radio | RxPower": ProfileMetricConfig(
            metric="Radio | RxPower",
            oid="signal_avg",
            sla_types=[],
            scale=1,
            units="dBm",
        ),
        "Radio | Roams": ProfileMetricConfig(
            metric="Radio | Roams",
            oid="roams_count",
            sla_types=[],
            scale=1,
            units="1",
        ),
        "Interface | Speed": ProfileMetricConfig(
            metric="Interface | Speed",
            oid="phy_rate_most_common",
            sla_types=[],
            scale=1,
            units="k,bit/s",
        ),
        # association_latency: 16786
        # authentication_latency: 110714
        # dhcp_latency: 1536500
        # total_latency: 3067500
        # traffic_latency: 657000
        # total_clients
        # association_ratio: 100
        # authentication_ratio: 100
        # dhcp_ratio: 100
        # dns_ratio: 100
        # success_ratio: 89
        # total_attempts: 41
    }

    def collect_cpe_metrics(self, metrics: List[MetricCollectorConfig]):
        """
        Collect metrics on client side(ONT).
        band: "na"
        channel: 116
        channel_width: "40"
        client: {fingerprint: {has_override: false}, hostname: "NB-1431", is_wired: false, mac: "bd:bd:bd:bd:bd:bd",…}
        last_ap_mac: "bd:bd:bd:bd:bd:bd"
        mimo: "MIMO_2"
        phy_mode_most_common:"ac"
        phy_rate_max: 39000
        phy_rate_most_common: 6000
        roams_count: 1
        satisfaction_avg: 95
        signal_avg: -88
        standard: "WIFI_5"
        total_traffic_percentage: 0
        tx_retries_percentage: 30.3
        """
        ts = self.get_ts()
        start = time.time()
        end = start + 70
        ape = {}
        # Group metric by port
        for probe in metrics:
            hints = probe.get_hints()
            _, mac = probe.labels[0].rsplit("::", 1)
            ape[mac] = probe
        if not ape:
            return
        # Client metrics
        # /v2/api/site/default/device?separateUnmanaged=true&includeTrafficUsage=true
        v = self.http.get(
            f"/v2/api/site/default/wifi-stats/details?start={round(start * 1_000)}&end={round(end * 1_1000)}&apMac=all",
            json=True,
        )
        for r in v["client_details"]:
            probe = r["last_ap_mac"]
            if probe not in ape:
                self.logger.warning("[%s] Unknown AP", probe)
                continue
            probe = ape[probe]
            labels = [
                f"noc::interface::0",
                f"noc::radio::standart::{r['standard']}",
                f"noc::wlan::band::{r['standard']}",
                f"noc::wlan::channel::{r['channel']}",
                f"noc::wlan::channel_width::{r['channel_width']}",
                f"noc::wlan::client::{r['client']['mac']}",
                f"noc::wlan::client::name::{r['client']['name']}",
            ]
            for m, mc in self.CPE_METRICS_CONFIG.items():
                if mc.oid not in r:
                    continue
                self.set_metric(
                    id=probe.cpe,
                    cpe=probe.cpe,
                    metric=m,
                    value=float(r[mc.oid]),
                    ts=ts,
                    labels=labels,
                    multi=True,
                    type="gauge",
                    scale=mc.scale,
                    units=mc.units,
                )
