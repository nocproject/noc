# ----------------------------------------------------------------------
# Stream Config class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Optional

# NOC modules
from .base import ConfigSection
from noc.core.config.params import (
    StringParameter,
    IntParameter,
    BooleanParameter,
    SecondsParameter,
    BytesParameter,
)


@dataclass(frozen=True)
class StreamConfig(object):
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
    partitions: Optional[int]
    shard: Optional[str] = None
    slot: Optional[str] = None
    enable: bool = True  # Stream is active
    config: Optional[StreamConfig] = None

    def get_partitions(self) -> int:
        return self.partitions

    @property
    def cursor_name(self) -> Optional[str]:
        name = self.slot or self.name
        if self.shard:
            return f"{name}.{self.shard}"
        return name

    def __str__(self):
        return self.name


class StreamConfigSection(ConfigSection):
    sharded = BooleanParameter(default=False)
    slot = StringParameter(default="", help="Name slots Config for stream partition number")
    partitions = IntParameter(default=0, min=0, help="Minimal number stream partitions")
    retention_max_age = SecondsParameter(
        default="24h",
        help="Retention interval for Stream. If 0 - default platform used",
    )
    retention_max_bytes = BytesParameter(
        default=0,
        help="Retention size (in bytes) for Stream. If 0 - default platform used",
    )
    segment_max_age = SecondsParameter(
        default="1h",
        help="Retention interval for Stream Segment. If 0 - default platform used",
    )
    segment_max_bytes = BytesParameter(
        default=0,
        help="Retention size (in bytes) for Stream Segment. If 0 - default platform used",
    )
    auto_pause_time = SecondsParameter(
        default=0,
        help="Time for after last message to stream, after pause stream processed  (for LiftBridge Applicable)",
    )
    auto_pause_disable_if_subscribers = BooleanParameter(default=False)
    replication_factor = IntParameter(default=0, min=0)

    @property
    def name(self):
        return self.__name__

    @classmethod
    def get_config(cls) -> StreamConfig:
        """"""
        return StreamConfig(
            retention_bytes=cls.retention_max_bytes,
            segment_bytes=cls.segment_max_bytes,
            retention_ages=cls.retention_max_age,
            segment_ages=cls.segment_max_age,
            auto_pause_time=cls.auto_pause_time,
            replication_factor=cls.replication_factor,
        )
