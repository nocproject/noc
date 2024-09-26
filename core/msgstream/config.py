# ----------------------------------------------------------------------
# Message Stream Config
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Optional, List

# NOC modules
from noc.config import config


@dataclass(frozen=True)
class StreamConfig(object):
    name: str
    sharded: bool = False
    slot: Optional[str] = None
    partitions: Optional[int] = None
    retention_bytes: int = 0
    segment_bytes: int = 0
    retention_ages: int = 86400
    segment_ages: int = 3600
    auto_pause_time: bool = False
    auto_pause_disable: bool = False
    replication_factor: Optional[int] = None


@dataclass(frozen=True)
class StreamItem(object):
    name: Optional[str]
    shard: Optional[str] = None  #
    slot: Optional[str] = None
    enable: bool = True  # Stream is active
    config: Optional[StreamConfig] = None

    def get_partitions(self) -> int:
        if self.config.partitions is not None:
            return self.config.partitions
        # Slot-based streams
        slot = self.slot or self.name
        if self.shard:
            slot = f"{slot}-{self.shard}"
        return config.get_slot_limits(slot)

    @property
    def cursor_name(self) -> Optional[str]:
        name = self.slot or self.name
        if self.shard:
            return f"{name}.{self.shard}"
        return name

    def __str__(self):
        return self.name


STREAMS: List[StreamConfig] = [
    StreamConfig(
        name="events",
        slot="classifier",
        sharded=True,
        retention_bytes=config.msgstream.events.retention_max_bytes,
        retention_ages=config.msgstream.events.retention_max_age,
        segment_bytes=config.msgstream.events.segment_max_bytes,
        segment_ages=config.msgstream.events.segment_max_age,
    ),
    StreamConfig(
        name="dispose",
        slot="correlator",
        sharded=True,
        retention_bytes=config.msgstream.dispose.retention_max_bytes,
        retention_ages=config.msgstream.dispose.retention_max_age,
        segment_bytes=config.msgstream.dispose.segment_max_bytes,
        segment_ages=config.msgstream.dispose.segment_max_age,
    ),
    StreamConfig(
        name="message",
        slot="mx",
        retention_bytes=config.msgstream.message.retention_max_bytes,
        retention_ages=config.msgstream.message.retention_max_age,
        segment_bytes=config.msgstream.message.segment_max_bytes,
        segment_ages=config.msgstream.message.retention_max_age,
    ),
    StreamConfig(name="revokedtokens", partitions=1),
    StreamConfig(
        name="jobs",
        slot="worker",
        retention_bytes=config.msgstream.jobs.retention_max_bytes,
        retention_ages=config.msgstream.jobs.retention_max_age,
        segment_bytes=config.msgstream.jobs.segment_max_bytes,
        segment_ages=config.msgstream.jobs.segment_max_age,
    ),
    StreamConfig(
        name="submit",
        partitions=1,
        retention_bytes=config.msgstream.submit.retention_max_bytes,
        retention_ages=config.msgstream.submit.retention_max_age,
        segment_bytes=config.msgstream.submit.segment_max_bytes,
        segment_ages=config.msgstream.submit.segment_max_age,
    ),
    StreamConfig(
        name="metrics",
        slot="metrics",
        replication_factor=1,
        retention_bytes=config.msgstream.metrics.retention_max_bytes,
        retention_ages=config.msgstream.metrics.retention_max_age,
        segment_bytes=config.msgstream.metrics.segment_max_bytes,
        segment_ages=config.msgstream.metrics.segment_max_age,
    ),
    StreamConfig(
        name="ch",
        sharded=True,
        partitions=len(config.clickhouse.cluster_topology.split(",")),
        replication_factor=1,
        retention_bytes=config.msgstream.ch.retention_max_bytes,
        retention_ages=config.msgstream.ch.retention_max_age,
        segment_bytes=config.msgstream.ch.segment_max_bytes,
        segment_ages=config.msgstream.ch.segment_max_age,
    ),
    # Sender
    StreamConfig(name="tgsender"),
    StreamConfig(name="mailsender"),
    StreamConfig(
        name="kafkasender",
        retention_bytes=config.msgstream.kafkasender.retention_max_bytes,
        retention_ages=config.msgstream.kafkasender.retention_max_age,
        segment_bytes=config.msgstream.kafkasender.segment_max_bytes,
        segment_ages=config.msgstream.kafkasender.segment_max_age,
    ),
]


def get_stream(name: str) -> StreamItem:
    cfg_name, *shard = name.split(".", 1)
    shard = shard[0] if shard else None
    cfg = [cfg for cfg in STREAMS if cfg.name == cfg_name]
    if not cfg:
        raise ValueError(f"[{name}] Unknown stream")
    if cfg[0].sharded and not shard:
        raise ValueError(f"[{name}] Shard name required for sharded stream")
    return StreamItem(name=name, shard=shard, slot=cfg[0].slot, config=cfg[0])
