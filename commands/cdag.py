# ----------------------------------------------------------------------
# CDAG utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
from collections import defaultdict
from typing import List

# Third-party modules
import orjson

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.cdag.graph import CDAG
from noc.core.service.loader import get_service


class Command(BaseCommand):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        # Args
        parser.add_argument("--config", help="Graph config path", action="append")
        # dot command
        dot = subparsers.add_parser("dot")
        dot.add_argument("--output", help="Output path")
        # metrics command
        metrics = subparsers.add_parser("metrics")
        metrics.add_argument("--input", help="Input path in JSONLine format")
        metrics.add_argument("--output", help="Output path in JSONLine format")

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_dot(self, config, output, *args, **kwargs):
        cdag = self.from_config_paths(config)
        with open(output, "w") as f:
            f.write(cdag.get_dot())

    def handle_metrics(self, config, input, output, *args, **kwargs):
        svc = get_service()
        cdag = self.from_config_paths(config)
        probes = {n.node_id: n for n in cdag.nodes.values() if n.name == "probe"}
        senders = {n for n in cdag.nodes.values() if n.name == "metrics"}
        default_units = {n.node_id: n.config.unit for n in probes.values()}
        skip_fields = {"ts", "labels", "_units"}
        key_fields = set()
        for s in senders:
            key_fields |= set(kf for kf in s.iter_unbound_inputs() if kf not in ("ts", "labels"))
        with open(input) as f, open(output, "wb") as fo:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = orjson.loads(line)
                tx = cdag.begin()
                units = data.get("_units") or {}
                ts = data["ts"]
                for n in data:
                    if n in skip_fields or n in key_fields:
                        continue
                    mu = units.get(n) or default_units[n]
                    probe = probes[n]
                    probe.activate(tx, "ts", ts)
                    probe.activate(tx, "x", data[n])
                    probe.activate(tx, "unit", mu)
                # Activate senders
                for sender in senders:
                    for kf in key_fields:
                        k = data.get(kf)
                        if k is not None:
                            sender.activate(tx, kf, k)
                    sender.activate(tx, "ts", ts)
                    sender.activate(tx, "labels", data.get("labels") or [])
                for scope in svc._metrics:
                    for m in svc._metrics[scope]:
                        fo.write(orjson.dumps(m))
                        fo.write(b"\n")
                # Reset metrics
                svc._metrics = defaultdict(list)

    def from_config_paths(self, paths: List[str]) -> CDAG:
        from noc.core.mongo.connection import connect

        connect()
        cdags = [self.from_config_path(path) for path in paths]
        cdag = cdags[0]
        for n, other in enumerate(cdags[1:]):
            cdag.merge(other, prefix=str(n))
        return cdag

    def from_config_path(self, path: str) -> CDAG:
        if path.startswith("scope://"):
            return self.from_metric_scope(path[8:])
        return self.from_config_file(path)

    def from_config_file(self, path: str) -> CDAG:
        with open(path) as f:
            cfg = f.read()
        ext = os.path.splitext(path)[1]
        if ext == ".json":
            return self.from_config_file_json(cfg)
        elif ext in (".yml", ".yaml"):
            return self.from_config_file_yaml(cfg)
        else:
            self.die("Unknown config format")

    @staticmethod
    def from_config_file_json(cfg: str) -> CDAG:
        from noc.core.cdag.factory.json import JSONCDAGFactory

        cdag = CDAG("test", {})
        factory = JSONCDAGFactory(cdag, cfg)
        factory.construct()
        return cdag

    @staticmethod
    def from_config_file_yaml(cfg: str) -> CDAG:
        from noc.core.cdag.factory.yaml import YAMLCDAGFactory

        cdag = CDAG("test", {})
        factory = YAMLCDAGFactory(cdag, cfg)
        factory.construct()
        return cdag

    def from_metric_scope(self, scope_name: str) -> CDAG:
        from noc.pm.models.metricscope import MetricScope
        from noc.core.cdag.factory.scope import MetricScopeCDAGFactory

        ms = MetricScope.objects.filter(name=scope_name).first()
        if not ms:
            self.die(f"Metric scope {scope_name} is not found")
        cdag = CDAG("test", {})
        factory = MetricScopeCDAGFactory(cdag, scope=ms, spool=False, sticky=True)
        factory.construct()
        return cdag


if __name__ == "__main__":
    Command().run()
