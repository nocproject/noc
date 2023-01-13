# ----------------------------------------------------------------------
# MsgStream Client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from typing import Optional, Dict, AsyncIterable

# NOC modules
from noc.core.msgstream.liftbridge import LiftBridgeClient
from noc.core.liftbridge.message import Message
from .config import get_stream
from .metadata import Metadata


logger = logging.getLogger(__name__)


class MessageStreamClient(object):
    """
    Client for Message Stream application (like Kafka)
    1. Access Messages
      * publish
      * subscribe
    2. Migration
      * Ensure Stream
    3. Processed Exception
      *
    4. Cursor API
      * fetch cursor
      * set cursor
    ? Namespace
    ? MessageQueueBuffer (SaveHeaders)
    """

    def __init__(self):
        self.client = LiftBridgeClient()

    async def __aenter__(self) -> "MessageStreamClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()

    async def subscribe(
        self,
        stream: str,
        partition: Optional[int] = None,
        start_offset: Optional[int] = None,
        start_timestamp: Optional[float] = None,
        resume: bool = False,
        cursor_id: Optional[str] = None,
        timeout: Optional[int] = None,
        allow_isr: bool = False,
    ) -> AsyncIterable[Message]:
        async for msg in self.client.subscribe(
            stream=stream,
            partition=partition,
            start_offset=start_offset,
            start_timestamp=start_timestamp,
            resume=resume,
            cursor_id=cursor_id,
            timeout=timeout,
        ):
            yield msg

    async def publish(
        self,
        value: bytes,
        stream: Optional[str] = None,
        key: Optional[bytes] = None,
        partition: Optional[int] = None,
        headers: Optional[Dict[str, bytes]] = None,
        ack_policy: int = 1,
        wait_for_stream: bool = False,
    ) -> None:
        # Build message
        await self.client.publish(
            value,
            stream=stream,
            key=key,
            partition=partition,
            headers=headers,
            ack_policy=ack_policy,
            wait_for_stream=wait_for_stream,
        )

    async def fetch_metadata(
        self, stream: Optional[str] = None, wait_for_stream: bool = False
    ) -> Metadata:
        return await self.client.fetch_metadata(stream, wait_for_stream=wait_for_stream)

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
        await self.client.create_stream(
            name=name,
            group=group,
            partitions=partitions,
            replication_factor=replication_factor,
        )

    async def delete_stream(self, name: str) -> None:
        await self.client.delete_stream(name)

    async def ensure_stream(self, name: str, partitions: Optional[int] = None) -> bool:
        """
        Ensure stream settings
        :param name:
        :param partitions:
        :return:
        """
        # Get stream config
        s = get_stream(name)
        # Get liftbridge metadata
        partitions = partitions or s.get_partitions()
        # Check if stream is configured properly
        if not partitions:
            logger.info("Stream '%s' without partition. Skipping..", name)
            return False
        meta = await self.fetch_metadata(name)
        rf = min(len(meta.brokers), 2)
        stream_meta = meta.metadata[name] if name in meta.metadata else None
        if stream_meta and len(stream_meta) == partitions:
            return False
        elif stream_meta:
            # Alter settings
            logger.info(
                "Altering stream %s due to partition/replication factor mismatch (%d -> %d)",
                name,
                len(stream_meta),
                partitions,
            )
            return await self.client.alter_stream(
                name, stream_meta, new_partitions=partitions, replication_factor=rf
            )
        logger.info("Creating stream %s with %s partitions", name, partitions)
        await self.create_stream(name, partitions=partitions, replication_factor=rf)
        return True

    async def fetch_cursor(self, stream: str, partition: int, cursor_id: str) -> int:
        """
        Getting stream cursor value
        :param stream:
        :param partition:
        :param cursor_id:
        :return:
        """
        return await self.client.fetch_cursor(stream, partition, cursor_id)

    async def set_cursor(self, stream: str, partition: int, cursor_id: str, offset: int) -> None:
        """
        Set stream cursor value
        :param stream:
        :param partition:
        :param cursor_id:
        :param offset:
        :return:
        """
        await self.client.set_cursor(stream, partition, cursor_id, offset=offset)
