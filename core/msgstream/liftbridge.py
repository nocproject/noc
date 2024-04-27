# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import random
from typing import Optional, Dict, AsyncIterable, Union
from collections import defaultdict

# Third-party modules
from gufo.liftbridge.client import LiftbridgeClient as GugoLiftbridgeClient
from gufo.liftbridge.types import StartPosition
from gufo.liftbridge.error import ErrorNotFound
from .message import Message

# NOC modules
from noc.config import config
from noc.core.msgstream.config import get_stream
from noc.core.ioloop.util import run_sync
from .metadata import Metadata, PartitionMetadata, Broker

logger = logging.getLogger(__name__)


class LiftBridgeClient(GugoLiftbridgeClient):
    SUBSCRIBE_BULK = False
    TIMESTAMP_MULTIPLIER = 1000_0000_00

    def __init__(self):
        broker = run_sync(self.resolve_broker)
        super().__init__(
            [broker],
            max_message_size=config.msgstream.max_message_size,
            compression_method=config.liftbridge.compression_method,
            compression_threshold=config.liftbridge.compression_threshold,
            publish_async_ack_timeout=config.liftbridge.publish_async_ack_timeout,
            enable_http_proxy=config.liftbridge.enable_http_proxy,
        )

    async def resolve_broker(self) -> str:
        # Getting addresses from config directly will block the loop on resolve() method.
        # So get parameter via .find_parameter() and resolve explicitly.
        addresses = await config.find_parameter("liftbridge.addresses").async_get()
        # Use random broker from seed
        svc = random.choice(addresses)
        return f"{svc.host}:{svc.port}"

    async def __aenter__(self) -> "LiftBridgeClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await super().__aexit__(exc_type, exc_val, exc_tb)

    @classmethod
    def get_replication_factor(cls, meta) -> int:
        return min(len(meta.brokers), 2)

    @staticmethod
    def get_topic_config(name, replication_factor: Optional[int] = 0) -> Dict[str, int]:
        """
        Return topic retention settings
        :param name:
        :param replication_factor:
        :return:
        """
        if name.startswith("__"):
            return {}
        s = get_stream(name)
        r = {}
        if s.config.replication_factor:
            replication_factor = min(s.config.replication_factor, replication_factor)
            r["minisr"] = min(2, replication_factor)
        r["replication_factor"] = replication_factor
        if s.config.retention_bytes:
            r["retention_max_bytes"] = s.config.retention_bytes
        if s.config.retention_ages:
            r["retention_max_age"] = s.config.retention_ages
        if s.config.segment_bytes:
            r["segment_max_bytes"] = s.config.segment_bytes
        if s.config.segment_ages:
            r["segment_max_age"] = s.config.segment_ages
        # "min.insync.replicas": 2,
        return r

    async def create_stream(
        self,
        name: str,
        group: Optional[str] = None,
        partitions: int = 0,
        replication_factor: int = 0,
        **kwargs,
    ) -> None:
        """
        Create Stream by settings
        :param name:
        :param group:
        :param partitions:
        :param replication_factor:
        :return:
        """
        await super().create_stream(
            name=name,
            group=group,
            partitions=partitions,
            **self.get_topic_config(name=name, replication_factor=replication_factor),
        )

    async def delete_stream(self, name: str):
        try:
            await super().delete_stream(name)
        except ErrorNotFound:
            pass

    async def fetch_metadata(
        self, stream: Optional[str] = None, wait_for_stream: bool = False
    ) -> Metadata:
        r = await self.get_metadata(stream=stream, wait_for_stream=wait_for_stream)
        s_meta = defaultdict(dict)
        for stream_m in r.metadata:
            for p, p_meta in stream_m.partitions.items():
                s_meta[stream_m.name][p] = PartitionMetadata(
                    topic=stream_m.name,
                    partition=p,
                    leader=p_meta.leader,
                    replicas=p_meta.replicas,
                    isr=p_meta.isr,
                )
        return Metadata(
            brokers=[Broker(id=b.id, host=b.host, port=b.port) for b in r.brokers],
            metadata=s_meta,
        )

    async def fetch_cursor(self, stream: str, partition: int, cursor_id: str) -> int:
        return await self.get_cursor(stream, partition, cursor_id)

    async def subscribe(
        self,
        stream: str,
        partition: Optional[int] = None,
        start_position: StartPosition = StartPosition.NEW_ONLY,
        start_offset: Optional[int] = None,
        start_timestamp: Optional[float] = None,
        resume: bool = False,
        cursor_id: Optional[str] = None,
        timeout: Optional[int] = None,
        allow_isr: bool = False,
        **kwargs,
    ) -> AsyncIterable[Message]:
        if cursor_id:
            start_position = StartPosition.RESUME
        async for msg in super().subscribe(
            stream=stream,
            partition=partition,
            start_position=start_position,
            start_offset=start_offset,
            start_timestamp=start_timestamp,
            resume=resume,
            cursor_id=cursor_id,
            timeout=timeout,
            allow_isr=allow_isr,
        ):
            yield msg

    async def fetch_partition_metadata(
        self, stream: str, partition: int, wait_for_stream: bool = False
    ) -> PartitionMetadata:
        return await self.get_partition_metadata(stream, partition, wait_for_stream)

    async def copy_topic_messages(
        self,
        from_topic,
        to_topic,
        partitions: Optional[Union[Dict[int, int], int]] = None,
    ) -> Dict[int, int]:
        """
        Copy message from one topic to another
        :param from_topic: From topic
        :param to_topic: To topic
        :param partitions: Number of from partition or MAP
        :return:
        """
        n_msg: Dict[int, int] = {}  # partition -> copied messages
        s = get_stream(from_topic)
        if not partitions:
            partitions = {0: 0}
        elif isinstance(partitions, int):
            partitions = {p: p for p in range(0, partitions)}
        elif not isinstance(partitions, dict):
            raise AttributeError("Partitions must be Int or Dict")
            # Copy all unread data to temporary stream as is
        for from_p, to_p in partitions.items():
            logger.info("Copying partition %s:%s to %s:%s", from_topic, from_p, to_topic, to_p)
            n_msg[to_p] = 0
            # Get current offset
            p_meta = await self.fetch_partition_metadata(from_topic, from_p)
            newest_offset = p_meta.newest_offset or 0
            # Fetch cursor
            current_offset = (
                await self.fetch_cursor(
                    stream=from_topic,
                    partition=from_p,
                    cursor_id=s.cursor_name,
                )
                or 0
            )
            # For -1 as nothing messages
            current_offset = max(0, current_offset)
            if current_offset > newest_offset:
                # Fix if cursor not set properly
                current_offset = newest_offset
            logger.info(
                "Start copying from current_offset: %s to newest offset: %s",
                current_offset,
                newest_offset,
            )
            if current_offset < newest_offset:
                async for msg in self.subscribe(
                    stream=from_topic, partition=from_p, start_offset=current_offset
                ):
                    await self.publish(
                        msg.value,
                        stream=to_topic,
                        partition=to_p,
                    )
                    n_msg[to_p] += 1
                    if msg.offset == newest_offset:
                        break
            if n_msg[to_p]:
                logger.info("  %d messages has been copied", n_msg[to_p])
            else:
                logger.info("  nothing to copy")
        return n_msg
