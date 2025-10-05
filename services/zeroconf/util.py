# ----------------------------------------------------------------------
# Utility functions
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Iterable
from collections import defaultdict

# NOC modules
from noc.core.tos import DSCP
from noc.pm.models.agent import Agent
from noc.sa.models.service import Service
from noc.inv.models.capability import Capability
from noc.inv.models.sensor import Sensor
from noc.main.models.label import Label
from noc.sla.models.slaprobe import SLAProbe
from .models.zk import (
    ZkConfig,
    ZkConfigConfig,
    ZkConfigConfigZeroconf,
    ZkConfigMetrics,
    ZkConfigCollector,
)

DEFAULT_MODBUS_TCP_PORT = 502
DEFAULT_MODBUS_TCP_SLAVE = 255


def find_agent(
    agent_id: Optional[str] = None,
    serial: Optional[str] = None,
    mac: Optional[List[str]] = None,
    ip: Optional[List[str]] = None,
):
    """
    Find agent by combination of credentials
    :param agent_id:
    :param serial:
    :param mac:
    :param ip:
    :return:
    """
    if agent_id:
        # Direct id is set
        return Agent.get_by_bi_id(int(agent_id))
    # Try serial
    agents: List[Agent] = []
    if serial:
        agents = list(Agent.objects.filter(serial=serial))
        if len(agents) == 1:
            # Exact match
            return agents[0]
    # No match or multiple matches, restrict to mac
    if mac:
        qs = Agent.objects.filter(mac__mac__in=mac)
        if agents:
            qs = qs.filter(bi_id__in=[a.bi_id for a in agents])
        agents = list(qs)
        if len(agents) == 1:
            # Exact match
            return agents[0]
    # No match or multiple matches, restrict to ip
    if ip:
        qs = Agent.objects.filter(ip__ip__in=ip)
        if agents:
            qs = qs.filter(bi_id__in=[a.bi_id for a in agents])
        agents = list(qs)
        if len(agents) == 1:
            # Exact match
            return agents[0]
    # Not found
    return None


def get_config(agent: Agent, level: int = 0, base: str = "") -> ZkConfig:
    """
    Generate agent config
    :param agent:
    :param level: Authorization level
    :param base: Base url
    :return:
    """
    check_interval = agent.get_effective_check_interval()
    is_disabled = not check_interval
    return ZkConfig(
        type="zeroconf",
        version="1",
        config=ZkConfigConfig(
            zeroconf=ZkConfigConfigZeroconf(
                id=agent.bi_id if level > 0 else None,
                key=agent.key if level > 0 else None,
                interval=300 if is_disabled else check_interval,
            ),
            metrics=ZkConfigMetrics(
                type="metricscollector",
                url=f"{base}/api/metricscollector/send",
            ),
        ),
        collectors=list(iter_collectors(agent)) if level >= 2 else [],
    )


def iter_collectors(agent: Agent) -> Iterable[ZkConfigCollector]:
    yield from iter_service_collectors(agent)
    yield from iter_sensor_collectors(agent)
    yield from iter_sla_collectors(agent)


def iter_service_collectors(agent: Agent) -> Iterable[ZkConfigCollector]:
    """
    Iterate over service settings
    :param agent:
    :return:
    """
    coll = Service._get_collection()
    for doc in coll.aggregate(
        [
            # Filter foot services for agent
            {"$match": {"agent": agent.id}},
            # Filter all descendant services
            {
                "$graphLookup": {
                    "from": coll.name,
                    "connectFromField": "_id",
                    "connectToField": "parent",
                    "startWith": "$_id",
                    "as": "children",
                    "maxDepth": 50,
                }
            },
            # Move root to children
            {
                "$project": {
                    "_id": 0,
                    "children": {
                        "$concatArrays": [
                            "$children",
                            [
                                {
                                    "_id": "$_id",
                                    "caps": "$caps",
                                    "bi_id": "$bi_id",
                                    "effective_labels": "$effective_labels",
                                }
                            ],
                        ]
                    },
                }
            },
            # Convert children to items
            {"$unwind": "$children"},
            {"$replaceRoot": {"newRoot": "$children"}},
            # Leave only necessary fields
            {"$project": {"_id": 0, "caps": 1, "effective_labels": 1, "bi_id": 1}},
        ]
    ):
        bi_id = doc.get("bi_id")
        if not bi_id:
            continue
        caps = doc.get("caps") or []
        collectors = defaultdict(dict)  # collector, scope -> key -> value
        # Extract collectors
        for c_doc in caps:
            caps_id = c_doc.get("capability") or None
            if not caps_id:
                continue
            c = Capability.get_by_id(caps_id)
            if not c or not c.agent_collector or not c.agent_param:
                continue
            value = c_doc.get("value") or None
            if value is None:
                continue
            scope = c_doc.get("scope") or ""
            collectors[c.agent_collector, scope][c.agent_param] = value
        # Process effective labels
        labels = Label.filter_labels(doc.get("effective_labels") or [], lambda x: x.expose_metric)
        # Filter out enabled scopes
        for (collector, scope), cfg in collectors.items():
            if not cfg.get("enabled", False):
                continue
            interval = cfg.get("interval", 0)
            if not interval:
                continue
            collector_id = f"zk:{bi_id}:{collector}:{scope}"
            e_cfg = {k: v for k, v in cfg.items() if k not in ("enabled", "interval")}
            yield ZkConfigCollector(
                id=collector_id,
                type=collector,
                service=bi_id,
                interval=interval,
                labels=labels,
                **e_cfg,
            )


def iter_sensor_collectors(agent: Agent) -> Iterable[ZkConfigCollector]:
    """
    Iterate over sensor settings
    :param agent:
    :return:
    """
    for sensor in Sensor.objects.filter(agent=agent.id):
        if not sensor.profile.enable_collect:
            continue
        if sensor.protocol == "modbus_rtu":
            yield from iter_modbus_rtu_collectors(sensor)
        elif sensor.protocol == "modbus_tcp" and sensor.managed_object:
            yield from iter_modbus_tcp_collectors(sensor)


def iter_modbus_rtu_collectors(sensor: Sensor) -> Iterable[ZkConfigCollector]:
    """
    Generate modbus_rtu collectors for sensor
    :param sensor:
    :return:
    """
    if not sensor.modbus_register or not sensor.modbus_format:
        return
    m_data = {
        d.attr: d.value for d in sensor.object.get_effective_data() if d.interface == "modbus"
    }
    yield ZkConfigCollector(
        id=f"zk:{sensor.bi_id}:modbus_rtu",
        type="modbus_rtu",
        service=sensor.bi_id,
        interval=sensor.profile.collect_interval,
        labels=[
            f"noc::sensor::{sensor.local_id}",
            *Label.filter_labels(sensor.effective_labels or [], lambda x: x.expose_metric),
        ],
        serial_path="/dev/ttyM0",
        slave=m_data["slave_id"],
        baud_rate=m_data["speed"],
        data_bits=m_data["bits"],
        # parity='None',
        stop_bits=m_data["stop"],
        register=sensor.modbus_register,
        format=sensor.modbus_format,
        disabled=not sensor.state.is_productive,
    )


def iter_modbus_tcp_collectors(sensor: Sensor) -> Iterable[ZkConfigCollector]:
    """
    Generate modbus_tcp collectors for sensor
    :param sensor:
    :return:
    """
    if not sensor.modbus_register or not sensor.modbus_format:
        return
    m_data = {
        d.attr: d.value for d in sensor.object.get_effective_data() if d.interface == "modbus"
    }
    yield ZkConfigCollector(
        id=f"zk:{sensor.bi_id}:modbus_tcp",
        type="modbus_tcp",
        service=sensor.bi_id,
        interval=sensor.profile.collect_interval,
        labels=[
            f"noc::sensor::{sensor.local_id}",
            *Label.filter_labels(sensor.effective_labels or [], lambda x: x.expose_metric),
        ],
        address=sensor.managed_object.address,
        port=sensor.managed_object.port or DEFAULT_MODBUS_TCP_PORT,
        slave=m_data["slave_id"] if m_data["slave_id"] != 16 else DEFAULT_MODBUS_TCP_SLAVE,
        register=sensor.modbus_register,
        format=sensor.modbus_format,
        disabled=not sensor.state.is_productive,
    )


def iter_sla_collectors(agent: Agent) -> Iterable[ZkConfigCollector]:
    """

    :param agent:
    :return:
    """
    for slaprobe in SLAProbe.objects.filter(agent=agent.id):
        server, port = slaprobe.target, 862
        if ":" in slaprobe.target:
            server, port = slaprobe.split(":")

        if slaprobe.type == "twamp":
            yield ZkConfigCollector(
                id=f"zk:{slaprobe.bi_id}:twamp_sender",
                type="twamp_sender",
                service=slaprobe.bi_id,
                interval=slaprobe.profile.metrics_default_interval,
                labels=[
                    f"noc::sla::name::{slaprobe.name}",
                    *Label.filter_labels(
                        slaprobe.effective_labels or [], lambda x: x.expose_metric
                    ),
                ],
                server=server,
                port=port,
                dscp=DSCP(slaprobe.tos).name,
                model="g711",
                # model="cbr",
                # model_bandwidth=1000000,
                # model_size=500,
                n_packets=slaprobe.profile.test_packets_num,
                disabled=not slaprobe.state.is_productive,
            )
