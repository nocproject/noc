# ----------------------------------------------------------------------
# CDAG utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import datetime
from collections import defaultdict
from typing import List, Optional, Iterable, Dict, Union

# Third-party modules
import orjson

# NOC modules
from noc.core.management.base import BaseCommand
from noc.core.cdag.graph import CDAG
from noc.core.service.loader import get_service


SQL = """
     SELECT ts, labels, %s FROM %s
     WHERE managed_object=%s and date >= '%s' and ts >= '%s' %s FORMAT JSONEachRow
"""

SQL_SLA = """
     SELECT ts, labels, %s FROM %s
     WHERE sla_probe=%s and date >= '%s' and ts >= '%s' %s FORMAT JSONEachRow
"""

NS = 1_000_000_000


class Command(BaseCommand):
    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        # Args
        parser.add_argument("--config", help="Graph config path", action="append", required=True)
        # dot command
        dot = subparsers.add_parser("dot")
        dot.add_argument("--output", help="Output path")
        # metrics command
        metrics = subparsers.add_parser("metrics")
        metrics.add_argument(
            "--input",
            dest="f_input",
            help="Input source url. File path in JSONLine format or Clickhouse: "
            "iface://<MONAME>::<IFACE_NAME>, cpu://<MONAME>, sla://<SLA_PROBE>",
        )
        metrics.add_argument("--output", dest="f_output", help="Output path in JSONLine format")

    def handle(self, cmd, *args, **options):
        return getattr(self, "handle_%s" % cmd)(*args, **options)

    def handle_dot(self, config, output: Optional[str] = None, *args, **kwargs):
        cdag = self.from_config_paths(config)
        if not output:
            self.print(cdag.get_dot())
            return
        with open(output, "w") as f:
            f.write(cdag.get_dot())

    @staticmethod
    def input_from_file(f_input: str) -> Iterable[Dict[str, Union[float, str]]]:
        with open(f_input) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                yield orjson.loads(line)

    def get_source(self, name, iface: Optional[str] = None):
        """
        Get source
        :param name:
        :param iface:
        :return:
        """
        from noc.core.mongo.connection import connect
        from noc.sa.models.managedobject import ManagedObject

        connect()

        source: ManagedObject = ManagedObject.objects.filter(name=name).first()
        if not source:
            self.die(f"Managed Object {name} is not found")
        if iface:
            source = source.get_interface(iface)
            if not source:
                self.die(f"Interface {iface} is not found")
        return source

    def input_from_device(self, source: str, metrics: List[str]):
        from noc.core.clickhouse.connect import connection
        from noc.sla.models.slaprobe import SLAProbe

        # now = datetime.datetime.now()
        # now = now - datetime.timedelta(hours=4)
        end = datetime.datetime(2022, 3, 1)
        start = end - datetime.timedelta(hours=4)
        q_args = []
        if source.startswith("iface://"):
            source, iface = source[8:].split("::")
            source = self.get_source(source, iface)
            query = SQL % (
                ",".join(metrics),
                "interface",
                source.managed_object.bi_id,
                start.date().isoformat(),
                start.replace(microsecond=0).isoformat(sep=" "),
                "AND interface=%s",
            )
            q_args += [source.name]
        elif source.startswith("cpu://"):
            source = source[6:]
            source = self.get_source(source)
            query = SQL % (
                "usage",
                "cpu",
                source.bi_id,
                start.date().isoformat(),
                start.replace(microsecond=0).isoformat(sep=" "),
                "",
            )
        elif source.startswith("sla://"):
            source = source[6:]
            sla = SLAProbe.get_by_id(source)
            # source = self.get_source(source)
            query = SQL_SLA % (
                ",".join(metrics),
                "sla",
                sla.bi_id,
                start.date().isoformat(),
                start.replace(microsecond=0).isoformat(sep=" "),
                "",
            )
        else:
            self.die(f"Unknown source {source}")
            return
        cursor = connection()
        r = cursor.execute(query, return_raw=True, args=q_args)
        for row in r.splitlines():
            row = orjson.loads(row)
            skip = False
            for k in row:
                if row[k] is None:
                    # Metrics not collected
                    skip = True
                    break
                if k == "labels":
                    continue
                elif k == "ts":
                    v = datetime.datetime.fromisoformat(row[k])
                    row[k] = int(v.timestamp() * NS)
                    continue
                row[k] = float(row[k])
            if skip:
                continue
            yield row

    def iter_metrics(
        self, f_input: Optional[str], metrics: Optional[List[str]] = None
    ) -> Iterable[Dict[str, Union[float, str]]]:
        if (
            f_input.startswith("cpu://")
            or f_input.startswith("iface://")
            or f_input.startswith("sla://")
        ):
            yield from self.input_from_device(f_input, metrics)
        else:
            yield from self.input_from_file(f_input)

    def handle_metrics(
        self,
        config,
        f_input: Optional[str] = None,
        f_output: Optional[str] = None,
        *args,
        **kwargs,
    ):
        svc = get_service()
        cdag = self.from_config_paths(config)
        probes = {n.node_id: n for n in cdag.nodes.values() if n.name == "probe"}
        # self.die("1")
        senders = {n for n in cdag.nodes.values() if n.name == "metrics"}
        dump = [n for n in cdag.nodes.values() if n.name == "dump"]
        if dump:
            dump = dump[0]
        default_units = {n.node_id: n.config.unit for n in probes.values()}
        skip_fields = {"ts", "labels", "_units"}
        key_fields = set()
        for s in senders:
            key_fields |= set(kf for kf in s.iter_unbound_inputs() if kf not in ("ts", "labels"))
        if f_output:
            f_output = open(f_output, "wb")
        for num, data in enumerate(self.iter_metrics(f_input, metrics=list(probes))):
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
                        if dump:
                            dump.activate(tx, kf, k)
                sender.activate(tx, "ts", ts)
                sender.activate(tx, "labels", data.get("labels") or [])
            # Dump value
            if dump:
                dump.activate(tx, "ts", ts)
                dump.activate(tx, "labels", data.get("labels") or [])
            for scope in svc._metrics:
                for m in svc._metrics[scope]:
                    if f_output:
                        f_output.write(orjson.dumps(m))
                        f_output.write(b"\n")
                    # self.print(orjson.dumps(m))
            # Reset metrics
            svc._metrics = defaultdict(list)
        if f_output:
            f_output.close()

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
        elif path.startswith("action://"):
            return self.from_metric_action(path[9:])
        return self.from_config_file(path)

    def from_metric_action(self, metric_action: str) -> CDAG:
        from noc.core.mongo.connection import connect
        from noc.core.cdag.factory.config import ConfigCDAGFactory
        from noc.pm.models.metricaction import MetricAction

        connect()
        ma: MetricAction = MetricAction.objects.filter(name=metric_action).first()
        if not ma:
            self.die(f"Metric Action {metric_action} is not found")
        cdag = CDAG("test", {})
        g_config = ma.get_config(enable_dump=True)
        for a_input in ma.compose_inputs:
            cdag.add_node(
                a_input.metric_type.field_name,
                node_type="probe",
                config={"unit": "1"},
                sticky=True,
            )
        f = ConfigCDAGFactory(cdag, g_config)
        f.construct()
        return cdag

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
