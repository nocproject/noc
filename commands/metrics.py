# ----------------------------------------------------------------------
# metrics uploading
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import argparse
import gzip
import os
import random
import datetime
import time
from dateutil.parser import parse
from functools import partial
from collections import defaultdict
from typing import List, Optional, Iterable, Dict, Union, Any, Tuple

# Third-party modules
import orjson

# NOC modules
from noc.config import config
from noc.core.management.base import BaseCommand
from noc.core.msgstream.client import MessageStreamClient
from noc.core.ioloop.util import run_sync
from noc.core.cdag.graph import CDAG
from noc.core.service.loader import get_service


SQL = """
     SELECT ts, labels, %s FROM %s
     WHERE managed_object=%s and date >= '%s' and ts >= '%s' and ts < '%s' %s FORMAT JSONEachRow
"""

NS = 1_000_000_000


class Command(BaseCommand):
    TOPIC = "chwriter"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="cmd", required=True)
        # load command
        load_parser = subparsers.add_parser("load", help="Load metrics to clickhouse")
        load_parser.add_argument("--fields", help="Data fields: <table>.<field1>.<fieldN>")
        load_parser.add_argument("--chunk", type=int, default=100_000, help="Size on chunk")
        load_parser.add_argument("--rm", action="store_true", help="Remove file after uploading")
        load_parser.add_argument("input", nargs=argparse.REMAINDER, help="Input files")
        cdag_dot_parser = subparsers.add_parser("cdag-dot")
        cdag_dot_parser.add_argument("--output", help="Output path")
        test_action = subparsers.add_parser("test-action")
        test_action.add_argument(
            "--config", help="Graph config path", action="append", required=True
        )
        test_action.add_argument(
            "--start", help="Start metric interval Time", dest="start", required=False
        )
        test_action.add_argument(
            "--end", help="End metric interval Time", dest="end", required=False
        )
        test_action.add_argument(
            "--input",
            dest="f_input",
            help="Input source url. File path in JSONLine format or Clickhouse: "
            "iface://<MONAME>::<IFACE_NAME>, cpu://<MONAME>, sla://<SLAPROBE_ID>",
        )
        test_action.add_argument("--output", dest="f_output", help="Output path in JSONLine format")
        test_service = subparsers.add_parser(
            "test-service", help="Send selected metrics to service"
        )
        test_service.add_argument(
            "--config", help="Graph config path", action="append", required=True
        )
        test_service.add_argument(
            "--start", help="Start metric interval Time", dest="start", required=False
        )
        test_service.add_argument(
            "--end", help="End metric interval Time", dest="end", required=False
        )
        test_service.add_argument(
            "--input",
            dest="f_input",
            help="Input source url. File path in JSONLine format or Clickhouse: "
            "iface://<MONAME>::<IFACE_NAME>, cpu://<MONAME>, sla://<SLAPROBE_ID>",
        )
        load_parser.add_argument("metrics", nargs=argparse.REMAINDER, help="Metrics")

    def handle(self, cmd, *args, **options):
        return getattr(self, f"handle_{cmd.replace('-', '_')}")(*args, **options)

    def get_source(self, source: str) -> Tuple[str, Any]:
        """
        Get source by input
        iface:<MONAME>::<IFACE_NAME>,
        mo:<MONAME>
        sla:<SLAPROBE_ID>
        :param source:
        :return:
        """
        from noc.core.mongo.connection import connect
        from noc.sa.models.managedobject import ManagedObject
        from noc.sla.models.slaprobe import SLAProbe

        connect()

        source, sid = source.split("://", 1)
        o = None
        if source == "mo":
            o: ManagedObject = ManagedObject.objects.filter(name=sid).first()
        elif source == "iface":
            mo_id, iface = sid.split("::")
            mo: ManagedObject = ManagedObject.objects.filter(name=mo_id).first()
            o = mo.get_interface(iface)
        elif source == "sla":
            o = SLAProbe.objects.filter(id=sid).first()
        elif source == "cpe":
            ...
        else:
            self.die(f"Unknown source {source}")
        if not source:
            self.die(f"Source {source}:{sid} is not found")
        return source, o

    def handle_cdag_dot(self, config, output: Optional[str] = None, *args, **kwargs):
        cdag = self.from_config_paths(config)
        if not output:
            self.print(cdag.get_dot())
            return
        with open(output, "w") as f:
            f.write(cdag.get_dot())

    def handle_load(self, fields, input, chunk, rm, *args, **kwargs):
        async def upload(table: str, data: List[bytes]):
            CHUNK = 1000
            n_parts = len(config.clickhouse.cluster_topology.split(","))
            async with MessageStreamClient() as client:
                while data:
                    chunk, data = data[:CHUNK], data[CHUNK:]
                    await client.publish(
                        "\n".join(chunk).encode(),
                        stream=f"ch.{table}",
                        partition=random.randint(0, n_parts - 1),
                    )

        for fn in input:
            # Read data
            self.print("Reading file %s" % fn)
            if fn.endswith(".gz"):
                with gzip.GzipFile(fn) as f:
                    records = f.read().replace("\r", "").splitlines()
            else:
                with open(fn) as f:
                    records = f.read().replace("\r", "").splitlines()
            table = fn.split("-", 1)[0]
            run_sync(partial(upload, table, records))
            if rm:
                os.unlink(fn)

    def input_from_device(
        self,
        source: str,
        metrics: List[str],
        start: Optional[datetime.datetime] = None,
        end: Optional[datetime.datetime] = None,
        register_metric: bool = False,
    ):
        """

        :param source:
        :param metrics:
        :param start:
        :param end:
        :param register_metric:
        :return:
        """
        from noc.core.clickhouse.connect import connection
        from noc.pm.models.metrictype import MetricType

        end = end or datetime.datetime.now()
        start = start or end - datetime.timedelta(hours=4)
        source, o = self.get_source(source)
        r = defaultdict(list)
        units = {}
        for mt in MetricType.objects.filter(field_name__in=metrics):
            r[mt.scope.table_name] += [mt.field_name]
            units[mt.field_name] = f"{mt.scale.code},{mt.units.code}"
        q_args = []
        for scope in r:
            f_sql = [",".join(r[scope]), scope]
            if scope in ["Interface", "sla"]:
                f_sql += [o.managed_object.bi_id]
            else:
                f_sql += [o.bi_id]
            f_sql += [
                start.date().isoformat(),
                start.replace(microsecond=0).isoformat(sep=" "),
                end.replace(microsecond=0).isoformat(sep=" "),
            ]
            if scope == "interface":
                f_sql += ["AND interface=%s"]
                q_args += [o.name]
            elif scope == "sla":
                f_sql += ["AND sla_probe=%s"]
                q_args += [o.bi_id]

            query = SQL % tuple(f_sql)
            self.print("QUERY", query)
            cursor = connection()
            r = cursor.execute(query, return_raw=True, args=q_args)
            data = {
                "_units": units,
                "managed_object": o.managed_object.bi_id,
                "sla_probe": o.bi_id,
                "scope": scope,
            }
            for row in r.splitlines():
                row = orjson.loads(row)
                if register_metric:
                    row.update(data)
                    yield row
                    continue
                for k in row:
                    if k == "labels":
                        continue
                    elif k == "ts":
                        v = datetime.datetime.fromisoformat(row[k])
                        row[k] = int(v.timestamp() * NS)
                        continue
                    row[k] = float(row[k])
                yield row

    def iter_metrics(
        self,
        f_input: Optional[str],
        metrics: Optional[List[str]] = None,
        start: Optional[datetime.datetime] = None,
        end: Optional[datetime.datetime] = None,
        register_metric: bool = False,
    ) -> Iterable[Dict[str, Union[float, str]]]:
        if ":" in f_input:
            yield from self.input_from_device(
                f_input, metrics, start=start, end=end, register_metric=register_metric
            )
        else:
            yield from self.input_from_file(f_input)

    def handle_test_action(
        self,
        config,
        f_input: Optional[str] = None,
        f_output: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        *args,
        **kwargs,
    ):
        """
        Test configured action
        :param config:
        :param f_input:
        :param f_output:
        :param start:
        :param end:
        :param args:
        :param kwargs:
        :return:
        """
        if end:
            end = parse(end)
        if start:
            start = parse(start)
        svc = get_service()
        cdag = self.from_config_paths(config)
        probes = {n.node_id: n for n in cdag.nodes.values() if n.name == "probe"}
        senders = {n for n in cdag.nodes.values() if n.name == "metrics"}
        dump = [n for n in cdag.nodes.values() if n.name == "dump"]
        if dump:
            dump = dump[0]
        default_units = {n.node_id: n.config.unit for n in probes.values()}
        skip_fields = {"ts", "labels", "_units"}
        key_fields = set()
        for s in senders:
            key_fields |= {kf for kf in s.iter_unbound_inputs() if kf not in ("ts", "labels")}
        if f_output:
            f_output = open(f_output, "wb")
        for data in self.iter_metrics(f_input, metrics=list(probes), start=start, end=end):
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

    def handle_test_service(
        self,
        config,
        f_input: Optional[str] = None,
        f_output: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        *args,
        **kwargs,
    ):
        async def upload(data: bytes):
            async with MessageStreamClient() as client:
                await client.publish(data, stream="metrics", partition=0)

        if end:
            end = parse(end)
        if start:
            start = parse(start)
        cdag = self.from_config_paths(config)
        probes = {n.node_id: n for n in cdag.nodes.values() if n.name == "probe"}
        for data in self.iter_metrics(
            f_input, metrics=list(probes), start=start, end=end, register_metric=True
        ):
            data["ts"] = time.time_ns()
            # data["managed_object"]
            # data["sla_probe"]
            run_sync(partial(upload, orjson.dumps([data])))
            time.sleep(5)
            self.print("Register Metric", data)

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
        if path.startswith("action://"):
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

    @staticmethod
    def input_from_file(f_input: str) -> Iterable[Dict[str, Union[float, str]]]:
        with open(f_input) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                yield orjson.loads(line)

    def from_config_file(self, path: str) -> CDAG:
        with open(path) as f:
            cfg = f.read()
        ext = os.path.splitext(path)[1]
        if ext == ".json":
            return self.from_config_file_json(cfg)
        if ext in (".yml", ".yaml"):
            return self.from_config_file_yaml(cfg)
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
