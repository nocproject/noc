# ----------------------------------------------------------------------
# MessageStream client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from typing import Optional, List, Dict, AsyncIterable
from dataclasses import dataclass

# NOC modules
from noc.core.handler import get_handler
from noc.config import config
from .message import Message, PublishRequest
from .queue import MessageStreamQueue

logger = logging.getLogger(__name__)


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


class BaseMessageStreamClient(object):
    async def __aenter__(self) -> "BaseMessageStreamClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """
        Close connections
        :return:
        """
        ...

    async def fetch_metadata(
        self, stream: Optional[str] = None, wait_for_stream: bool = False
    ) -> Metadata:
        """

        :param stream:
        :param wait_for_stream:
        :return:
        """
        ...

    async def fetch_partition_metadata(
        self, stream: str, partition: int, wait_for_stream: bool = False
    ) -> PartitionMetadata:
        """

        :param stream:
        :param partition:
        :param wait_for_stream:
        :return:
        """
        ...

    async def create_stream(
        self,
        subject: str,
        name: str,
        group: Optional[str] = None,
        replication_factor: int = 1,
        minisr: int = 0,
        partitions: int = 1,
        enable_compact: bool = False,
        retention_max_age: int = 0,
        retention_max_bytes: int = 0,
        segment_max_age: int = 0,
        segment_max_bytes: int = 0,
        auto_pause_time: int = 0,
        auto_pause_disable_if_subscribers: bool = False,
    ):
        """

        :param subject:
        :param name:
        :param group:
        :param replication_factor:
        :param minisr:
        :param partitions:
        :param enable_compact:
        :param retention_max_age:
        :param retention_max_bytes:
        :param segment_max_age:
        :param segment_max_bytes:
        :param auto_pause_time:
        :param auto_pause_disable_if_subscribers:
        :return:
        """
        ...

    async def delete_stream(self, name: str) -> None:
        """

        :param name:
        :return:
        """
        ...

    async def publish(
        self,
        value: bytes,
        stream: Optional[str] = None,
        key: Optional[bytes] = None,
        partition: Optional[int] = None,
        headers: Optional[Dict[str, bytes]] = None,
        ack_inbox: Optional[str] = None,
        correlation_id: Optional[str] = None,
        ack_policy: Optional[int] = None,
        wait_for_stream: bool = False,
        auto_compress: bool = False,
    ) -> None:
        """

        :param value:
        :param stream:
        :param key:
        :param partition:
        :param headers:
        :param ack_inbox:
        :param correlation_id:
        :param ack_policy:
        :param wait_for_stream:
        :param auto_compress:
        :return:
        """
        ...

    async def subscribe(
        self,
        stream: str,
        partition: Optional[int] = None,
        start_position: Optional[int] = None,
        start_offset: Optional[int] = None,
        start_timestamp: Optional[float] = None,
        resume: bool = False,
        cursor_id: Optional[str] = None,
        timeout: Optional[int] = None,
        allow_isr: bool = False,
    ) -> AsyncIterable[Message]:
        """

        :param stream:
        :param partition:
        :param start_position:
        :param start_offset:
        :param start_timestamp:
        :param resume:
        :param cursor_id:
        :param timeout:
        :param allow_isr:
        :return:
        """
        ...

    async def fetch_cursor(self, stream: str, partition: int, cursor_id: str) -> int:
        """

        :param stream:
        :param partition:
        :param cursor_id:
        :return:
        """
        ...

    async def set_cursor(self, stream: str, partition: int, cursor_id: str, offset: int) -> None:
        """

        :param stream:
        :param partition:
        :param cursor_id:
        :param offset:
        :return:
        """

    @classmethod
    def get_queue(cls):
        """
        Return Queue object for publish message
        :return:
        """
        return MessageStreamQueue

    @staticmethod
    def get_publish_request(
        value: bytes,
        stream: Optional[str] = None,
        key: Optional[bytes] = None,
        partition: Optional[int] = None,
        headers: Optional[Dict[str, bytes]] = None,
        auto_compress: bool = False,
        **kwargs,
    ) -> PublishRequest:
        """
        Create publish request for queue
        :param value: Message body
        :param stream: Stream
        :param key: Sharding key
        :param partition: Partition for publish
        :param headers:
        :param auto_compress:
        :return:
        """
        return PublishRequest(
            message=value,
            stream=stream,
            partition=partition,
            key=key,
            headers=headers or {},
            auto_compress=auto_compress,
        )

    @classmethod
    def get_client(cls) -> "BaseMessageStreamClient":
        """
        Return client for queue
        :return:
        """
        logger.info("Using StreamClient backend: %s", config.message.client_class)
        # c = get_handler(config.cache.cache_class)
        c = get_handler(config.message.client_class)
        if c:
            return c
        else:
            logger.error("Cannot load cache backend: Fallback to dummy")
            return BaseMessageStreamClient


# client singleton
stream_client = BaseMessageStreamClient.get_client()
