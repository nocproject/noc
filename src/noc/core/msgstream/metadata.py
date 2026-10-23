# ----------------------------------------------------------------------
# MsgStream Metadata
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from collections.abc import Iterable


@dataclass(frozen=True)
class Broker:
    id: str
    host: str
    port: int


@dataclass(frozen=True)
class PartitionMetadata:
    topic: str
    partition: int
    leader: str
    # The ids of all brokers that contain replicas of the partition
    replicas: list[str]
    # The ids of all brokers that contain in-sync replicas of the partition
    isr: list[int] | None = None
    error: str | None = None
    high_watermark: int | None = None
    newest_offset: int | None = None

    @property
    def id(self):
        return f"{self.topic}.{self.partition}"


@dataclass(frozen=True)
class Metadata:
    brokers: list[Broker]
    metadata: dict[str, dict[int, PartitionMetadata]]  # Stream -> Partition -> PartitionMetadata

    def iter_partitions(self) -> Iterable[PartitionMetadata]:
        for stream in self.metadata:
            yield from self.metadata[stream].values()
