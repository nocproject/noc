# ---------------------------------------------------------------------
# Eltex.MA4000.get_metrics
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
from collections import defaultdict
from typing import List

# NOC modules
from noc.sa.profiles.Generic.get_metrics import Script as GetMetricsScript, ProfileMetricConfig
from noc.core.models.cfgmetrics import MetricCollectorConfig
from noc.core.text import parse_kv, list_to_ranges


class Script(GetMetricsScript):
    name = "Eltex.MA4000.get_metrics"

    splitter = re.compile(r"\s*-+\n")

    kv_map = {
        "voltage": "Interface | DOM | Voltage",
        "bias current": "Interface | DOM | Bias Current",
        "temperature": "Interface | DOM | Temperature",
        "tx power": "Interface | DOM | TxPower",
        "rx power": "Interface | DOM | RxPower",
    }

    CPE_METRICS_CONFIG = {
        "Interface | DOM | Temperature": ProfileMetricConfig(
            metric="Interface | DOM | Temperature",
            oid="",
            sla_types=[],
            scale=1,
            units="C",
        ),
        "Interface | DOM | TxPower": ProfileMetricConfig(
            metric="Interface | DOM | TxPower",
            oid="",
            sla_types=[],
            scale=1,
            units="dBm",
        ),
        "Interface | DOM | RxPower": ProfileMetricConfig(
            metric="Interface | DOM | RxPower",
            oid="",
            sla_types=[],
            scale=1,
            units="dBm",
        ),
        "Interface | DOM | Voltage": ProfileMetricConfig(
            metric="Interface | DOM | Voltage",
            oid="",
            sla_types=[],
            scale=1,
            units="VDC",
        ),
        "Interface | DOM | Bias Current": ProfileMetricConfig(
            metric="Interface | DOM | Bias Current",
            oid="",
            sla_types=[],
            scale=1,
            units="m,A",
        ),
    }

    def collect_cpe_metrics(self, metrics: List[MetricCollectorConfig]):
        """
        Collect metrics on client side(ONT).
        """
        ont_ifaces = defaultdict(dict)
        ts = self.get_ts()
        # Group metric by port
        for probe in metrics:
            hints = probe.get_hints()
            slot, port, ont_id = hints["local_id"].split("/")
            ont_ifaces[(slot, port)][ont_id] = probe
        if not ont_ifaces:
            return
        for iface, ont_ids in ont_ifaces.items():
            slot, port = iface
            try:
                c = self.cli(
                    f"show interface ont {slot}/{port}/{list_to_ranges([int(x) for x in ont_ids])} laser"
                )
            except self.CLISyntaxError:
                raise NotImplementedError
            parts = self.splitter.split(c)
            parts = parts[1:]
            while len(parts) > 1:
                (header, body), parts = parts[:2], parts[2:]
                if len(body) <= 100:
                    continue
                data = parse_kv(self.kv_map, body)
                cpe_id = header.split("[")[-1].split("]")[0].lower()
                slot, port, ont_id = cpe_id.split("/")
                if ont_id not in ont_ids:
                    continue
                probe = ont_ids[ont_id]
                for m, mc in self.CPE_METRICS_CONFIG.items():
                    if mc.metric not in data or data[mc.metric] == "n/a":
                        continue
                    self.set_metric(
                        id=probe.cpe,
                        cpe=probe.cpe,
                        metric=m,
                        value=float(data[mc.metric].split()[0]),
                        ts=ts,
                        labels=[*probe.labels, "noc::interface::0"],
                        multi=True,
                        type="gauge",
                        scale=mc.scale,
                        units=mc.units,
                    )
