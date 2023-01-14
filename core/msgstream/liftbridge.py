# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import random
from typing import Optional, Dict, AsyncIterable
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
    def __init__(self):
        broker = run_sync(self.resolve_broker)
        super().__init__([broker])

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

    @staticmethod
    def get_topic_config(name, replication_factor: Optional[int] = 0) -> Dict[str, int]:
        """
        Return topic retention settings
        :param name:
        :param replication_factor:
        :return:
        """
        s = get_stream(name)
        r = {}
        minisr = 0
        if s.config.replication_factor:
            replication_factor = min(s.config.replication_factor, replication_factor)
            minisr = min(2, replication_factor)
        r["minisr"] = minisr
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

    async def alter_stream(
        self,
        name: str,
        current_meta: Dict[int, PartitionMetadata],
        new_partitions: Optional[int] = None,
        replication_factor: Optional[int] = None,
    ) -> bool:
        old_partitions = len(current_meta)
        n_msg: Dict[int, int] = {}  # partition -> copied messages
        s = get_stream(name)
        logger.info("Altering stream %s", name)
        # Create temporary stream with same structure, as original one
        tmp_stream = f"__tmp-{name}"
        logger.info("Creating temporary stream %s", tmp_stream)
        try:
            await self.delete_stream(tmp_stream)
        except ErrorNotFound:
            pass
        await super().create_stream(
            subject=tmp_stream,
            name=tmp_stream,
            partitions=old_partitions,
            replication_factor=1,
        )
        # Copy all unread data to temporary stream as is
        for partition in range(old_partitions):
            logger.info("Copying partition %s:%s to %s:%s", name, partition, tmp_stream, partition)
            n_msg[partition] = 0
            # Get current offset
            p_meta = await self.get_partition_metadata(name, partition)
            newest_offset = p_meta.newest_offset or 0
            # Fetch cursor
            current_offset = await self.get_cursor(
                stream=name,
                partition=partition,
                cursor_id=s.cursor_name,
            )
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
                    stream=name, partition=partition, start_offset=current_offset
                ):
                    await self.publish(
                        msg.value,
                        stream=tmp_stream,
                        partition=partition,
                    )
                    n_msg[partition] += 1
                    if msg.offset == newest_offset:
                        break
            if n_msg[partition]:
                logger.info("  %d messages has been copied", n_msg[partition])
            else:
                logger.info("  nothing to copy")
        # Drop original stream
        logger.info("Dropping original stream %s", name)
        await self.delete_stream(name)
        # Create new stream with required structure
        logger.info("Creating stream %s", name)
        await super().create_stream(
            subject=name,
            name=name,
            partitions=new_partitions,
            replication_factor=replication_factor,
        )
        # Copy data from temporary stream to a new one
        for partition in range(old_partitions):
            logger.info("Restoring partition %s:%s to %s" % (tmp_stream, partition, new_partitions))
            # Re-route dropped partitions to partition 0
            dest_partition = partition if partition < new_partitions else 0
            n = n_msg[partition]
            if n > 0:
                async for msg in self.subscribe(
                    stream=tmp_stream,
                    partition=partition,
                    start_position=StartPosition.EARLIEST,
                ):
                    await self.publish(msg.value, stream=name, partition=dest_partition)
                    n -= 1
                    if not n:
                        break
                logger.info("  %s messages restored", n_msg[partition])
            else:
                logger.info("  nothing to restore")
        # Drop temporary stream
        logger.info("Dropping temporary stream %s", tmp_stream)
        await self.delete_stream(tmp_stream)
        # Uh-oh
        logger.info("Stream %s has been altered", name)
        return True

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
    ) -> AsyncIterable[Message]:
        if cursor_id:
            start_position = StartPosition.RESUME
        print("SS", start_position, cursor_id)
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
