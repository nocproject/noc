# ----------------------------------------------------------------------
# Metrics collection simulation
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.cdag.graph import CDAG
from noc.core.cdag.factory.yaml import YAMLCDAGFactory

CONFIG = """
nodes:
- name: load_in
  description: load_in probe
  type: probe
  config:
    unit: bit/s
- name: load_out
  description: load_out probe
  type: probe
  config:
    unit: bit/s
- name: speed
  description: speed probe
  type: probe
  config:
    unit: bit/s
- name: in_rel
  description: Input relative load
  type: div
  inputs:
    - name: x
      node: load_in
    - name: y
      node: speed
- name: out_rel
  description: Output relative load
  type: div
  inputs:
    - name: x
      node: load_out
    - name: y
      node: speed
- name: total_load
  description: Input + output load
  type: add
  inputs:
    - name: x
      node: load_in
    - name: y
      node: load_out
- name: sender
  description: metrics sender
  type: metrics
  config:
    scope: interface
    spool: false
  inputs:
    - name: load_in
      node: load_in
      dynamic: true
    - name: load_out
      node: load_out
      dynamic: true
    - name: speed
      node: speed
      dynamic: true
    - name: rel_in
      node: in_rel
      dynamic: true
    - name: rel_out
      node: out_rel
      dynamic: true
    - name: total_load
      node: total_load
      dynamic: true
- name: check
  description: Metrics checking point
  type: none
  inputs:
    - name: x
      node: sender
"""

NS = 1_000_000_000
TS = 1621847580000000000
TS_STR = "2021-05-24 09:13:00"
DATE = "2021-05-24"
STEP = 10 * NS
LABELS = ["noc::interface::Fa 0/1"]
SPEED = 100_000_000
UNITS = {"load_in": "byte", "load_out": "byte"}


def ts_str(n: int) -> str:
    return f"{TS_STR[:-2]}{n * 10:02d}"


SCENARIO = [
    # input metrics, output metrics or None
    (
        {
            "ts": TS,
            "labels": LABELS,
            "load_in": 1_000,
            "load_out": 2_000,
            "speed": SPEED,
            "_units": UNITS,
        },
        # load_in and load_out are not activated, as counters
        {
            "date": DATE,
            "ts": ts_str(0),
            "labels": LABELS,
            "speed": SPEED,
        },
    ),
    (
        {
            "ts": TS + STEP,
            "labels": LABELS,
            "load_in": 2_000,
            "load_out": 2_500,
            "speed": SPEED,
            "_units": UNITS,
        },
        # load_in and load_out are activated
        {
            "date": DATE,
            "ts": ts_str(1),
            "labels": LABELS,
            "load_in": 800,
            "load_out": 400,
            "total_load": 1200.0,
            "rel_in": 8e-6,
            "rel_out": 4e-6,
            "speed": SPEED,
        },
    ),
    (
        {
            "ts": TS + 2 * STEP,
            "labels": LABELS,
            "load_in": 3_000,
            "speed": SPEED,
            "_units": UNITS,
        },
        # load_out is missed, skipping rel_out, total_load
        {
            "date": DATE,
            "ts": ts_str(2),
            "labels": LABELS,
            "load_in": 800.0,
            "speed": SPEED,
            "rel_in": 8e-6,
        },
    ),
    (
        {
            "ts": TS + 3 * STEP,
            "labels": LABELS,
            "load_in": 4_000,
            "load_out": 3_500,
            "speed": SPEED,
            "_units": UNITS,
        },
        # load_out is restored
        {
            "date": DATE,
            "ts": ts_str(3),
            "labels": LABELS,
            "load_in": 800.0,
            "load_out": 400.0,
            "speed": SPEED,
            "rel_in": 8e-6,
            "rel_out": 4e-6,
            "total_load": 1200.0,
        },
    ),
    # No metrics
    (
        {
            "ts": TS + 3 * STEP,
            "labels": LABELS,
            "_units": UNITS,
        },
        None,
    ),
]


def test_case():
    state = {}
    cdag = CDAG("test", state=state)
    factory = YAMLCDAGFactory(cdag, CONFIG)
    factory.construct()
    sender = cdag.nodes["sender"]
    probes = {n.node_id: n for n in cdag.nodes.values() if n.name == "probe"}
    default_units = {n.node_id: n.config.unit for n in probes.values()}
    skip_fields = {"ts", "labels", "_units"}
    for data, expected in SCENARIO:
        print(data)
        tx = cdag.begin()
        # Activate metrics
        units = data.get("_units") or {}
        ts = data["ts"]
        for n in data:
            if n in skip_fields:
                continue
            mu = units.get(n) or default_units[n]
            probe = probes[n]
            probe.activate(tx, "ts", ts)
            probe.activate(tx, "x", data[n])
            probe.activate(tx, "unit", mu)
        # Activate sender
        sender.activate(tx, "target", None)
        sender.activate(tx, "ts", ts)
        sender.activate(tx, "labels", data["labels"])
        result = tx.inputs.get(cdag.nodes["check"]) or None
        if result:
            result = result["x"]
        if expected is None:
            assert result is None
        else:
            assert result == expected


def setup_module(_module):
    from noc.core.cdag.node.probe import ProbeNode

    ProbeNode.set_convert(
        {
            # Name -> alias -> expr
            "bit": {"byte": "x * 8"},
            "bit/s": {
                "byte/s": "x * 8",
                "bit": "delta / time_delta",
                "byte": "delta * 8 / time_delta",
            },
        }
    )


def teardown_module(_module):
    from noc.core.cdag.node.probe import ProbeNode

    ProbeNode.reset_convert()
