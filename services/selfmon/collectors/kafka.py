# ----------------------------------------------------------------------
# Kafka Collector
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List, Tuple, Optional, Dict, DefaultDict, Iterable
import struct
from dataclasses import dataclass
from collections import defaultdict


# Third-party modules
from aiokafka import AIOKafkaClient, AIOKafkaConsumer, TopicPartition

# NOC modules
from .base import BaseCollector, Metric
from noc.core.ioloop.util import run_sync
from noc.config import config

# Primitive data parsers
UINT16 = struct.Struct("!H")
UINT32 = struct.Struct("!I")
COMMIT_VALUE = struct.Struct("!HQ")


@dataclass
class PartitionCursor(object):
    group: str
    topic_partition: TopicPartition


@dataclass
class PartitionOffset(object):
    topic_partition: TopicPartition
    end_offset: int
    cursors: Dict[str, int]


class KafkaStreamCollector(BaseCollector):
    name = "kafka"

    TOPIC_CURSORS = {
        "events": "classifier",
        "dispose": "correlator",
        "message": "mx",
        "kafkasender": "kafkasender",
        "jobs": "worker",
        "metrics": "metrics",
    }
    CLIENT_ID = "NOC"

    async def get_partitions(self, bootstrap_servers: List[str]) -> List[TopicPartition]:
        client = AIOKafkaClient(bootstrap_servers=bootstrap_servers, client_id=self.CLIENT_ID)
        await client.bootstrap()
        # Get all partitions
        r = await client.fetch_all_metadata()
        partitions = []
        for topic_partitions in r._partitions.values():
            for partition_meta in topic_partitions.values():
                partitions.append(partition_meta)
        # Get offsets
        return [TopicPartition(p.topic, p.partition) for p in partitions]

    async def get_offsets(
        self, bootstrap_servers: List[str], partitions: List[TopicPartition]
    ) -> List[PartitionOffset]:
        ch_cluster = config.clickhouse.cluster_topology.split(",")
        async with AIOKafkaConsumer(
            bootstrap_servers=bootstrap_servers,
            client_id=self.CLIENT_ID,
            enable_auto_commit=False,
            auto_offset_reset="earliest",
        ) as consumer:
            # Get last offsets for all partitions
            end_offsets = await consumer.end_offsets(partitions)
        # Fetch offsets
        offsets: DefaultDict[TopicPartition, Dict[str, int]] = defaultdict(dict)
        #
        offset_groups: DefaultDict[str, List[TopicPartition]] = defaultdict(list)
        for p in partitions:
            if p.topic.startswith("ch."):
                for replica in range(0, int(ch_cluster[p.partition])):
                    offset_groups[f"chwriter-{replica}"].append(p)
                continue
            if "." in p.topic:
                name = p.topic.split(".", 1)[0]
            else:
                name = p.topic
            if name in self.TOPIC_CURSORS:
                offset_groups[self.TOPIC_CURSORS[name]].append(p)
        for g, parts in offset_groups.items():
            async with AIOKafkaConsumer(
                bootstrap_servers=bootstrap_servers,
                group_id=g,
                client_id=self.CLIENT_ID,
                enable_auto_commit=False,
            ) as consumer:
                r = await consumer._coordinator.fetch_committed_offsets(parts)
                for pp, offset in r.items():
                    offsets[pp][g] = offset.offset
        return [
            PartitionOffset(topic_partition=p, end_offset=end_offsets[p], cursors=offsets[p])
            for p in partitions
            if not p.topic.startswith("__")
        ]

    @staticmethod
    def parse_cursor_key(key: bytes) -> Optional[PartitionCursor]:
        """Parse kafka cursor key."""

        def parse_uint16(k: bytes) -> Tuple[int, bytes]:
            (v,) = UINT16.unpack(k[:2])
            return v, k[2:]

        def parse_uint32(k: bytes) -> Tuple[int, bytes]:
            (v,) = UINT32.unpack(k[:4])
            return v, k[4:]

        def parse_str(k: bytes) -> Tuple[str, bytes]:
            str_len, rest = parse_uint16(k)
            return rest[:str_len].decode(), rest[str_len:]

        version, rest = parse_uint16(key)
        if version != 1:
            return None
        group, rest = parse_str(rest)
        topic, rest = parse_str(rest)
        partition, _ = parse_uint32(rest)
        return PartitionCursor(
            topic_partition=TopicPartition(topic=topic, partition=partition), group=group
        )

    @staticmethod
    def parse_cursor_offset(value: bytes) -> Optional[int]:
        version, offset = COMMIT_VALUE.unpack(value[:10])
        if version != 3:
            return None
        return offset

    async def collect(self) -> List[PartitionOffset]:
        addresses = await config.find_parameter("redpanda.addresses").async_get()
        bootstrap_servers = [f"{svc.host}:{svc.port}" for svc in addresses]
        partitions = await self.get_partitions(bootstrap_servers)
        return await self.get_offsets(bootstrap_servers, partitions)

    def iter_metrics(self) -> Iterable[Metric]:
        offsets = run_sync(self.collect)
        ch_cluster = config.clickhouse.cluster_topology.split(",")
        for pd in offsets:
            topic = pd.topic_partition.topic
            partition = pd.topic_partition.partition
            if topic.startswith("__"):
                continue
            is_clickhouse = topic.startswith("ch.")
            if "." in topic and not is_clickhouse:
                name, pool = topic.split(".", 1)
            else:
                name, pool = topic, None
            # Cursor
            if is_clickhouse:
                for replica in range(0, int(ch_cluster[partition])):
                    cursor_id = f"chwriter-{replica}"
                    yield self.metric(
                        "stream_cursor_offset",
                        name=topic,
                        partition=partition,
                        cursor_id=cursor_id,
                        value=pd.cursors.get(cursor_id, 0),
                    )
            else:
                cursor_name = self.TOPIC_CURSORS.get(name)
                if cursor_name and cursor_name in pd.cursors:
                    yield self.metric(
                        "stream_cursor_offset",
                        pool=pool,
                        name=topic,
                        partition=partition,
                        cursor_id=self.TOPIC_CURSORS[name],
                        value=pd.cursors[cursor_name],
                    )
            # Partition
            yield self.metric(
                "stream_newest_offset",
                pool=pool,
                name=topic,
                partition=partition,
                value=pd.end_offset,
            )
            yield self.metric(
                "stream_high_watermark",
                pool=pool,
                name=topic,
                partition=partition,
                value=pd.end_offset,
            )
