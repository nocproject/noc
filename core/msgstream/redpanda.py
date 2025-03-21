# ----------------------------------------------------------------------
# RedPanda client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import asyncio
import random
from typing import Optional, Dict, AsyncIterable, List, Union
from collections import defaultdict

# Third-party modules
from aiokafka.producer.producer import AIOKafkaProducer
from aiokafka.consumer.consumer import AIOKafkaConsumer, TopicPartition
from aiokafka.structs import OffsetAndTimestamp
from aiokafka.client import AIOKafkaClient
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import (
    KafkaError,
    KafkaTimeoutError,
    UnknownTopicOrPartitionError,
    NodeNotReadyError,
    KafkaConnectionError,
    MessageSizeTooLargeError,
)

# NOC Modules
from noc.core.perf import metrics
from noc.config import config
from noc.core.ioloop.util import run_sync
from noc.core.timeout import retry_timeout
from .config import get_stream
from .metadata import Metadata, PartitionMetadata, Broker
from .message import Message
from .error import MsgStreamError

logger = logging.getLogger(__name__)

CLIENT_ID = "NOC"


class RedPandaClient(object):
    TIMESTAMP_MULTIPLIER = 1_000
    SUBSCRIBE_BULK = True

    def __init__(self):
        self.bootstrap = None
        self.producer: Optional[AIOKafkaProducer] = None
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.client: Optional[AIOKafkaClient] = None
        self.admin_client: Optional[AIOKafkaAdminClient] = None
        self.loop = asyncio.get_running_loop()
        self.stub = None
        kafka_logger = logging.getLogger("kafka")
        kafka_logger.setLevel(logging.WARN)

    @classmethod
    async def resolve_broker(cls) -> str:
        # Getting addresses from config directly will block the loop on resolve() method.
        # So get parameter via .find_parameter() and resolve explicitly.
        addresses = await config.find_parameter("redpanda.addresses").async_get()
        # Use random broker from seed
        svc = random.choice(addresses)
        return f"{svc.host}:{svc.port}"

    def get_bootstrap(self) -> str:
        if not self.bootstrap:
            self.bootstrap = run_sync(self.resolve_broker)
        return self.bootstrap

    async def __aenter__(self) -> "RedPandaClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """
        Close connections
        :return:
        """
        if self.producer:
            await self.producer.stop()
            self.producer = None
        if self.consumer:
            # Workaround for Issue aiokafka/issues/647
            await asyncio.sleep(0.1)
            await self.consumer.stop()
            self.consumer = None
        if self.admin_client:
            await self.admin_client.close()
            self.admin_client = None
        if self.client:
            await self.client.close()

    @classmethod
    def get_replication_factor(cls, meta) -> int:
        """
        Only Odd number, Max 3. Maybe config ?
        """
        return min(len(meta.brokers), 3) or 1

    async def fetch_metadata(
        self, stream: Optional[str] = None, wait_for_stream: bool = False
    ) -> Metadata:
        """
        Fetch cluster metadata
        :param stream: topic name
        :param wait_for_stream: Wait for cluster init
        :return:
        """
        client = self.get_kafka_client()
        await client.bootstrap()
        s_meta: Dict[str, Dict[int, PartitionMetadata]] = defaultdict(dict)
        req_parts = []
        r = await client.fetch_all_metadata()
        for stream_n, stream_m in r._partitions.items():
            if stream and stream_n != stream:
                continue
            for p, p_meta in stream_m.items():
                req_parts.append(TopicPartition(topic=stream_n, partition=p))
                s_meta[stream_n][p] = PartitionMetadata(
                    topic=stream_n,
                    partition=p,
                    leader=p_meta.leader,
                    replicas=list(p_meta.replicas),
                    isr=list(p_meta.isr),
                )
        return Metadata(
            brokers=[Broker(id=b.nodeId, host=b.host, port=b.port) for b in r.brokers()],
            metadata=s_meta,
        )

    async def fetch_partition_metadata(
        self, stream: str, partition: int, wait_for_stream: bool = False
    ) -> PartitionMetadata:
        con = await self.get_consumer()
        tp = TopicPartition(topic=stream, partition=partition)
        con.assign([tp])
        # Fetch newest offset
        offsets = await con.end_offsets([tp])
        return PartitionMetadata(
            topic=stream,
            partition=partition,
            leader=con._client.cluster.leader_for_partition(tp),
            replicas=list(con._client.cluster._partitions[stream][partition].replicas),
            isr=list(con._client.cluster._partitions[stream][partition].isr),
            high_watermark=offsets[tp],
            newest_offset=offsets[tp],
        )

    async def get_producer(self) -> AIOKafkaProducer:
        """
        Returns connected kafka producer
        :return:
        """
        if self.producer:
            return self.producer
        bootstrap = self.get_bootstrap()
        logger.info("Connecting to producer using bootstrap services %s", bootstrap)
        self.producer = AIOKafkaProducer(
            loop=self.loop,
            bootstrap_servers=bootstrap,
            acks=1,
            max_batch_size=config.redpanda.max_batch_size,
            sasl_mechanism=config.redpanda.sasl_mechanism,
            security_protocol=config.redpanda.security_protocol,
            sasl_plain_username=config.redpanda.username,
            sasl_plain_password=config.redpanda.password,
            max_request_size=config.redpanda.max_request_size,
            compression_type=(
                None
                if config.redpanda.compression_type == "none"
                else config.redpanda.compression_type
            ),
        )
        while True:
            try:
                logger.info("Try starting producer")
                await self.producer.start()
                break
            except (KafkaConnectionError, NodeNotReadyError) as e:
                # KafkaConnectionError: No connection to node with id 1
                metrics["errors", ("type", "kafka_producer_start")] += 1
                logger.error("Failed to connect producer: %s", e)
            await retry_timeout(10.0, name="kafka_producer")
        return self.producer

    async def get_consumer(self, group_id=None) -> AIOKafkaConsumer:
        if self.consumer:
            return self.consumer
        self.consumer = AIOKafkaConsumer(
            loop=self.loop,
            bootstrap_servers=self.get_bootstrap(),
            client_id=CLIENT_ID,
            enable_auto_commit=False,
            group_id=group_id,
            retry_backoff_ms=config.redpanda.retry_backoff_ms * 1_000,
        )
        while True:
            # @todo errors
            try:
                await self.consumer.start()
                return self.consumer
            except KafkaConnectionError as e:
                logger.error("Cannot connect to Kafka: %s", e)
                await retry_timeout(1.0, name="kafka_consumer")

    def get_kafka_client(self) -> AIOKafkaClient:
        """
        Return Async Kafka Client
        :return:
        """
        if not self.client:
            self.client = AIOKafkaClient(
                bootstrap_servers=self.get_bootstrap(), client_id=CLIENT_ID
            )  # config.client_id
        return self.client

    async def get_kafka_admin_client(self) -> AIOKafkaAdminClient:
        """
        Return Kafka Admin Client
        :return:
        """
        if not self.admin_client:
            self.admin_client = AIOKafkaAdminClient(
                bootstrap_servers=self.get_bootstrap(), client_id=CLIENT_ID
            )  # config.client_id
            await self.admin_client.start()
        return self.admin_client

    @staticmethod
    def get_topic_config(name, replication_factor: int = 1) -> Dict[str, str]:
        """
        Return topic retention settings
        :param name:
        :param replication_factor: Cluster replicator factor
        :return:
        """
        if name.startswith("__"):
            return {}
        cfg = get_stream(name)
        # Replica not more 3
        isr = min(cfg.config.replication_factor or 3, replication_factor or 1) - 1
        r = {
            "min.insync.replicas": max(isr, 1),
        }
        if cfg.config.retention_bytes:
            r["retention.bytes"] = str(cfg.config.retention_bytes)
        if cfg.config.retention_ages:
            r["retention.ms"] = str(cfg.config.retention_ages * 1000)
        if cfg.config.segment_bytes:
            r["segment.bytes"] = str(cfg.config.segment_bytes)
        if cfg.config.segment_ages:
            r["segment.ms"] = str(cfg.config.segment_ages * 1000)
        return r or None

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
        admin_client = await self.get_kafka_admin_client()
        await admin_client.create_topics(
            new_topics=[
                NewTopic(
                    name=name,
                    num_partitions=partitions,
                    replication_factor=replication_factor,
                    topic_configs=self.get_topic_config(name, replication_factor),
                )
            ],
            validate_only=False,
        )

    async def delete_stream(self, name: str) -> None:
        """
        Delete topic by name
        :param name: Topic name
        :return:
        """
        admin_client = await self.get_kafka_admin_client()
        try:
            await admin_client.delete_topics([name])
        except UnknownTopicOrPartitionError:
            pass

    async def _subscribe(
        self,
        streams: List[str],
        group_id: str,
        partition: Optional[int] = None,
        start_offset: Optional[int] = None,
        start_timestamp: Optional[float] = None,
        resume: bool = True,
        cursor_id: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        """

        Client Example:
        # consumer = AIOKafkaConsumer(
        #     bootstrap_servers='10.10.10.20:9092,10.10.10.19:9092,10.10.10.21:9092'
        # )
        # consumer = AIOKafkaConsumer(
        #     loop=loop, bootstrap_servers='localhost:9092',
        #     metadata_max_age_ms=5000, group_id="test2")
        # consumer.seek(TopicPartition('my_topic', 0), msg.offset)
        # consumer.subscribe(pattern="test*")
        # # Get cluster layout and topic/partition allocation
        # await consumer.start()
        # try:
        #     async for msg in consumer:
        #         print(msg.value)
        # finally:
        #     await consumer.stop()

        :param streams: Topic list
        :param partition: Partition num (for manual assign)
        :param start_offset: Offset for staring read
        :param start_timestamp: Timestamp for staring read
        :param resume:
        :param cursor_id:
        :param timeout:
        :param allow_isr:
        :return:
        """
        consumer = await self.get_consumer(group_id=group_id)
        if partition is not None:
            consumer.assign(
                [TopicPartition(topic=stream, partition=partition) for stream in streams]
            )
        else:
            consumer.subscribe(topics=streams)
        if not resume:
            return
        for tp in consumer.assignment():
            if start_offset is not None:
                consumer.seek(tp, start_offset)
            elif start_timestamp is not None:
                offset: Dict[TopicPartition, OffsetAndTimestamp] = await consumer.offsets_for_times(
                    {tp: start_timestamp}
                )
                consumer.seek(tp, offset[tp].offset)
            else:
                logger.debug("Getting stored offset for stream '%s'", tp)
                r = await consumer.seek_to_committed(tp)
                if r[tp] is not None:
                    logger.info("Resuming from offset %d", r[tp])
                else:
                    await consumer.seek_to_end(tp)

    def __aiter__(self):
        return self

    async def __anext__(self):
        consumer = await self.get_consumer()
        msg = await consumer.__anext__()
        return Message(
            value=msg.value,
            subject=msg.topic,
            offset=msg.offset,
            timestamp=msg.timestamp,
            key=msg.key,
            partition=msg.partition,
            headers=dict(msg.headers),
        )

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
        """
        For compatible NOC Client method
        :param stream:
        :param partition:
        :param start_offset:
        :param start_timestamp:
        :param resume:
        :param cursor_id:
        :param timeout:
        :param allow_isr:
        :return:
        """
        # async with consumer as c:
        await self._subscribe(
            streams=[stream],
            group_id=stream,
            partition=partition,
            start_offset=start_offset,
            start_timestamp=start_timestamp,
            resume=resume,
            cursor_id=cursor_id,
            timeout=timeout,
        )
        async for msg in self:
            yield msg

    async def publish(
        self,
        value: bytes,
        stream: Optional[str] = None,
        key: Optional[bytes] = None,
        partition: Optional[int] = None,
        headers: Optional[Dict[str, bytes]] = None,
        **kwargs,
    ) -> None:
        """
        Publish message to stream
        :param value:
        :param stream:
        :param key:
        :param partition:
        :param headers:
        :param kwargs:
        :return:
        """
        logger.debug("Sending to topic %s", stream)
        producer = await self.get_producer()
        headers = headers or {}
        try:
            await producer.send(
                stream,
                value,
                key=key,
                partition=partition,
                headers=[(k, v) for k, v in headers.items()],
            )
            producer.create_batch()
            metrics["messages_sent_ok", ("topic", stream)] += 1
            metrics["bytes_sent", ("topic", stream)] += len(value)
        except KafkaTimeoutError as e:
            logger.error("Timeout when sending to topic: %s", stream)
            raise MsgStreamError(str(e))
        except MessageSizeTooLargeError as e:
            metrics["messages_sent_error", ("topic", stream)] += 1
            logger.error("Failed to send to topic %s: %s", stream, str(e))
        except KafkaError as e:
            metrics["messages_sent_error", ("topic", stream)] += 1
            logger.error("Failed to send to topic %s: %s", stream, e)
            if e.invalid_metadata:
                # Retry getting metadata
                await producer.stop()
                self.producer = None
            elif e.retriable:
                # Retry message
                raise MsgStreamError(str(e))
            raise e  # Unknown error

    async def fetch_cursor(self, stream: str, partition: int, cursor_id: str) -> int:
        """
        Fetch cursor offset for stream
        :param stream: Topic name
        :param partition: Partition number
        :param cursor_id:
        :return:
        """
        consumer = await self.get_consumer(group_id=stream)
        return await consumer.committed(TopicPartition(topic=stream, partition=partition))

    async def set_cursor(self, stream: str, partition: int, cursor_id: str, offset: int) -> None:
        """
        Setting cursor offset for stream
        :param stream: Topic name
        :param partition: Partition number
        :param cursor_id:
        :param offset:
        :return:
        """
        logger.debug("[%s|%s] Set cursor to1: %s", stream, partition, offset)
        consumer = await self.get_consumer(group_id=stream)
        if TopicPartition(topic=stream, partition=partition) not in consumer.assignment():
            consumer.assign([TopicPartition(topic=stream, partition=partition)])
        await consumer.commit({TopicPartition(topic=stream, partition=partition): offset})

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
        :param partitions: Number of from partition
        :return:
        """
        n_msg: Dict[int, int] = {}  # partition -> copied messages
        if not partitions:
            partitions = {0: 0}
        elif isinstance(partitions, int):
            partitions = {p: p for p in range(0, partitions)}
        elif not isinstance(partitions, dict):
            raise AttributeError("Partitions must be Int or Dict")
        consumer = AIOKafkaConsumer(
            loop=self.loop,
            bootstrap_servers=self.bootstrap,
            client_id=CLIENT_ID,
            enable_auto_commit=False,
            group_id=from_topic,
        )
        consumer.subscribe(topics=[from_topic])
        await consumer.start()
        for from_p, to_p in partitions.items():
            logger.info("Copying partition %s:%s to %s:%s", from_topic, from_p, to_topic, to_p)
            n_msg[to_p] = 0
            # Get current offset
            p_meta = await self.fetch_partition_metadata(from_topic, from_p)
            newest_offset = p_meta.newest_offset or 0
            # Fetch cursor
            tp = TopicPartition(topic=from_topic, partition=from_p)
            r = await consumer.seek_to_committed(tp)
            if r[tp] is not None:
                logger.info("Resuming from offset %d", r[tp])
            else:
                continue
            current_offset = r[tp]
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
                async for msg in consumer:
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
        await consumer.stop()
        return n_msg
