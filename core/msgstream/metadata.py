# ----------------------------------------------------------------------
# MsgStream Metadata
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Optional, Dict, List, Iterable


@dataclass(frozen=True)
class Broker(object):
    id: str
    host: str
    port: int


@dataclass(frozen=True)
class PartitionMetadata(object):
    topic: str
    partition: int
    leader: str
    # The ids of all brokers that contain replicas of the partition
    replicas: List[str]
    # The ids of all brokers that contain in-sync replicas of the partition
    isr: Optional[List[int]] = None
    error: Optional[str] = None
    high_watermark: Optional[int] = None
    newest_offset: Optional[int] = None

    @property
    def id(self):
        return f"{self.topic}.{self.partition}"


@dataclass(frozen=True)
class Metadata(object):
    brokers: List[Broker]
    metadata: Dict[str, Dict[int, PartitionMetadata]]  # Stream -> Partition -> PartitionMetadata

    def iter_partitions(self) -> Iterable[PartitionMetadata]:
        for stream in self.metadata:
            for part_meta in self.metadata[stream].values():
                yield part_meta
