# ----------------------------------------------------------------------
# Message Stream models
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Optional, Dict, List

# NOC modules
from noc.config import config


@dataclass
class Broker(object):
    id: str
    host: str
    port: int


@dataclass
class PartitionMetadata(object):
    id: int
    leader: str
    replicas: List[str]
    isr: List[str]
    high_watermark: int
    newest_offset: int
    paused: bool


@dataclass
class StreamMetadata(object):
    name: str
    subject: str
    partitions: Dict[int, PartitionMetadata]


@dataclass
class Metadata(object):
    brokers: List[Broker]
    metadata: List[StreamMetadata]


@dataclass(frozen=True)
class RetentionPolicy(object):
    retention_bytes: int = 0
    segment_bytes: int = 0
    retention_ages: int = 86400
    segment_ages: int = 3600


@dataclass(frozen=True)
class StreamConfig(object):
    name: Optional[str] = None  #
    shard: Optional[str] = None  #
    partitions: Optional[int] = None  # Partition numbers
    slot: Optional[str] = None  # Configured slots
    pooled: bool = False
    cursor: Optional[str] = None  # Cursor name
    enable: bool = True  # Stream is active
    auto_pause_time: bool = False
    auto_pause_disable: bool = False
    replication_factor: Optional[int] = None
    retention_policy: RetentionPolicy = RetentionPolicy()

    def get_partitions(self) -> int:
        from noc.core.service.loader import get_service

        if self.partitions is not None:
            return self.partitions

        # Slot-based streams
        svc = get_service()
        return svc.get_slot_limits(f"{self.slot}-{self.shard}" if self.shard else self.slot)

    @property
    def cursor_name(self) -> Optional[str]:
        return self.cursor or self.slot

    @property
    def stream_name(self):
        if self.shard:
            return f"{self.name}.{self.shard}"
        return self.name

    def __str__(self):
        return self.name


STREAM_CONFIG: Dict[str, StreamConfig] = {
    "events": StreamConfig(
        slot="classifier",
        pooled=True,
        retention_policy=RetentionPolicy(
            retention_bytes=config.liftbridge.stream_events_retention_max_bytes,
            retention_ages=config.liftbridge.stream_events_retention_max_age,
            segment_bytes=config.liftbridge.stream_events_segment_max_bytes,
            segment_ages=config.liftbridge.stream_events_segment_max_age,
        ),
    ),
    "dispose": StreamConfig(
        slot="correlator",
        pooled=True,
        retention_policy=RetentionPolicy(
            retention_bytes=config.liftbridge.stream_dispose_retention_max_bytes,
            retention_ages=config.liftbridge.stream_dispose_retention_max_age,
            segment_bytes=config.liftbridge.stream_dispose_segment_max_bytes,
            segment_ages=config.liftbridge.stream_dispose_segment_max_age,
        ),
    ),
    "message": StreamConfig(
        slot="mx",
        retention_policy=RetentionPolicy(
            retention_bytes=config.liftbridge.stream_message_retention_max_bytes,
            retention_ages=config.liftbridge.stream_message_retention_max_age,
            segment_bytes=config.liftbridge.stream_message_segment_max_bytes,
            segment_ages=config.liftbridge.stream_message_retention_max_age,
        ),
    ),
    "revokedtokens": StreamConfig(partitions=1),
    "jobs": StreamConfig(
        slot="worker",
        retention_policy=RetentionPolicy(
            retention_bytes=config.liftbridge.stream_jobs_retention_max_bytes,
            retention_ages=config.liftbridge.stream_jobs_retention_max_age,
            segment_bytes=config.liftbridge.stream_jobs_segment_max_bytes,
            segment_ages=config.liftbridge.stream_jobs_segment_max_age,
        ),
    ),
    "metrics": StreamConfig(
        slot="metrics",
        replication_factor=1,
        retention_policy=RetentionPolicy(
            retention_bytes=config.liftbridge.stream_metrics_retention_max_bytes,
            retention_ages=config.liftbridge.stream_metrics_retention_max_age,
            segment_bytes=config.liftbridge.stream_metrics_segment_max_bytes,
            segment_ages=config.liftbridge.stream_metrics_segment_max_age,
        ),
    ),
    "ch": StreamConfig(
        partitions=len(config.clickhouse.cluster_topology.split(",")),
        slot=None,
        replication_factor=1,
        retention_policy=RetentionPolicy(
            retention_bytes=config.liftbridge.stream_ch_retention_max_bytes,
            retention_ages=config.liftbridge.stream_ch_retention_max_age,
            segment_bytes=config.liftbridge.stream_ch_segment_max_bytes,
            segment_ages=config.liftbridge.stream_ch_segment_max_age,
        ),
    ),
    # Sender
    "tgsender": StreamConfig(name="tgsender", slot="tgsender"),
    "icqsender": StreamConfig(name="icqsender", slot="icqsender"),
    "mailsender": StreamConfig(name="mailsender", slot="mailsender"),
    "kafkasender": StreamConfig(
        name="kafkasender",
        slot="kafkasender",
        retention_policy=RetentionPolicy(
            retention_bytes=config.liftbridge.stream_kafkasender_retention_max_bytes,
            retention_ages=config.liftbridge.stream_kafkasender_retention_max_age,
            segment_bytes=config.liftbridge.stream_kafkasender_segment_max_bytes,
            segment_ages=config.liftbridge.stream_kafkasender_segment_max_age,
        ),
    ),
}


def get_stream_config(name: str) -> StreamConfig:
    cfg_name, *shard = name.split(".", 1)
    base_cfg = None
    if cfg_name in STREAM_CONFIG:
        base_cfg = STREAM_CONFIG[cfg_name]
    return StreamConfig(
        name=name,
        enable=base_cfg.enable if base_cfg else True,
        shard=shard[0] if shard else None,
        partitions=base_cfg.partitions if base_cfg else None,
        slot=base_cfg.slot if base_cfg else None,
        replication_factor=base_cfg.replication_factor if base_cfg else None,
        retention_policy=base_cfg.retention_policy if base_cfg else RetentionPolicy(),
    )
