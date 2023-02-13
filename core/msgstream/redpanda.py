# ----------------------------------------------------------------------
# RedPanda client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
import asyncio
from typing import Optional, Dict, AsyncIterable
from collections import defaultdict

# Third-party modules
from aiokafka.producer.producer import AIOKafkaProducer
from aiokafka.consumer.consumer import AIOKafkaConsumer, TopicPartition
from aiokafka.structs import OffsetAndTimestamp
from aiokafka.client import AIOKafkaClient
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import (
    KafkaError,
    UnknownTopicOrPartitionError,
    NodeNotReadyError,
    KafkaConnectionError,
)

# NOC Modules
from noc.core.perf import metrics
from noc.config import config
from .config import get_stream
from .metadata import Metadata, PartitionMetadata, Broker
from .message import Message, PublishRequest

logger = logging.getLogger(__name__)

CLIENT_ID = "NOC"


class RedPandaClient(object):
    TIMESTAMP_MULTIPLIER = TS_NS = 1_000

    def __init__(self):
        self.bootstrap = config.redpanda.bootstrap_servers.split(",")
        self.producer: Optional[AIOKafkaProducer] = None
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.client: Optional[AIOKafkaClient] = None
        self.admin_client: Optional[KafkaAdminClient] = None
        self.loop = asyncio.get_running_loop()
        self.stub = None

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
        # if self.admin_client:
        #    self.admin_client.close()
        # if self.client:
        #    await self.client.close()

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
        s_meta = defaultdict(dict)
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
        # Fetch newest offset
        # con = await self.get_consumer()
        # await con.start()
        # offsets = await con.end_offsets(req_parts)
        # for tp, offset in offsets.items():
        #     s_meta[tp.topic][tp.partition].newest_offset = offset
        #     s_meta[tp.topic][tp.partition].high_watermark = offset
        return Metadata(
            brokers=[Broker(id=b.nodeId, host=b.host, port=b.port) for b in r.brokers()],
            metadata=s_meta,
        )

    async def get_producer(self) -> AIOKafkaProducer:
        """
        Returns connected kafka producer
        :return:
        """
        if self.producer:
            return self.producer
        # bootstrap = [x.strip() for x in config.kafkasender.bootstrap_servers.split(",")]
        logger.info("Connecting to producer using bootstrap services %s", self.bootstrap)
        self.producer = AIOKafkaProducer(
            loop=self.loop,
            bootstrap_servers=self.bootstrap,
            acks=1,
            max_batch_size=config.redpanda.max_batch_size,
            sasl_mechanism=config.redpanda.sasl_mechanism,
            security_protocol=config.redpanda.security_protocol,
            sasl_plain_username=config.redpanda.username,
            sasl_plain_password=config.redpanda.password,
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
            await asyncio.sleep(10)
        return self.producer

    async def get_consumer(self, group_id=None) -> AIOKafkaConsumer:
        if self.consumer:
            return self.consumer
        self.consumer = AIOKafkaConsumer(
            loop=self.loop,
            bootstrap_servers=self.bootstrap,
            client_id=CLIENT_ID,
            enable_auto_commit=False,
            group_id=group_id,
            retry_backoff_ms=config.redpanda.retry_backoff_ms * 1_000,
        )
        # @todo errors
        await self.consumer.start()
        return self.consumer

    def get_kafka_client(self) -> AIOKafkaClient:
        """
        Return Async Kafka Client
        :return:
        """
        if not self.client:
            self.client = AIOKafkaClient(
                bootstrap_servers=self.bootstrap, client_id=CLIENT_ID
            )  # config.client_id
        return self.client

    def get_kafka_admin_client(self) -> KafkaAdminClient:
        """
        Return Kafka Admin Client
        :return:
        """
        if not self.admin_client:
            self.admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap, client_id=CLIENT_ID
            )  # config.client_id
        return self.admin_client

    @staticmethod
    def get_topic_config(name) -> Dict[str, str]:
        """
        Return topic retention settings
        :param name:
        :return:
        """
        cfg = get_stream(name)
        r = {}
        if cfg.config.retention_bytes:
            r["retention.bytes"] = str(cfg.config.retention_bytes)
        if cfg.config.retention_ages:
            r["retention.ms"] = str(cfg.config.retention_ages * 1000)
        if cfg.config.segment_bytes:
            r["segment.bytes"] = str(cfg.config.segment_bytes)
        if cfg.config.segment_ages:
            r["segment.ms"] = str(cfg.config.segment_ages * 1000)
        # "min.insync.replicas": 2,
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
        admin_client = self.get_kafka_admin_client()
        admin_client.create_topics(
            new_topics=[
                NewTopic(
                    name=name,
                    num_partitions=partitions,
                    replication_factor=replication_factor,
                    topic_configs=self.get_topic_config(name),
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
        admin_client = self.get_kafka_admin_client()
        try:
            admin_client.delete_topics([name])
        except UnknownTopicOrPartitionError:
            pass

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

        :param stream: Topic name
        :param partition: Partition num (for manual assign)
        :param start_offset: Offset for staring read
        :param start_timestamp: Timestamp for staring read
        :param resume:
        :param cursor_id:
        :param timeout:
        :param allow_isr:
        :return:
        """
        consumer = await self.get_consumer(group_id=stream)
        if partition is not None:
            consumer.assign([TopicPartition(topic=stream, partition=partition)])
        else:
            consumer.subscribe(topics=[stream])
        tp: TopicPartition = next(iter(consumer.assignment()), None)
        if not tp:
            return
        if start_offset is not None:
            consumer.seek(tp, start_offset)
        elif start_timestamp is not None:
            offset: Dict[TopicPartition, OffsetAndTimestamp] = await consumer.offsets_for_times(
                {tp: start_timestamp}
            )
            consumer.seek(tp, offset[tp].offset)
        else:
            logger.info("Getting stored offset for stream '%s'", stream)
            r = await consumer.seek_to_committed(tp)
            if r[tp] is not None:
                logger.info("Resuming from offset %d", r[tp])
            else:
                await consumer.seek_to_end(tp)
        # async with consumer as c:
        async for msg in consumer:
            logger.info("Consume message")
            yield Message(
                value=msg.value,
                subject=msg.topic,
                offset=msg.offset,
                timestamp=msg.timestamp,
                key=msg.key,
                partition=msg.partition,
                headers=msg.headers,
            )
            if cursor_id:
                await consumer.commit(
                    {TopicPartition(msg.topic, partition=msg.partition): msg.offset + 1}
                )

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
        except KafkaError as e:
            metrics["messages_sent_error", ("topic", stream)] += 1
            logger.error("Failed to send to topic %s: %s", stream, e)
        finally:
            await producer.stop()
            self.producer = None

    async def publish_sync(self, req: PublishRequest, wait_for_stream: bool = False) -> None:
        """
        Send publish request and wait for acknowledge
        :param req:
        :param wait_for_stream: Wait for stream being created.
        :return:
        """
        await self.publish(req.data, req.stream, req.key, req.partition, req.headers)

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
        Settint cursor offset for stream
        :param stream: Topic name
        :param partition: Partition number
        :param cursor_id:
        :param offset:
        :return:
        """
        consumer = await self.get_consumer(group_id=stream)
        consumer.assign([TopicPartition(topic=stream, partition=partition)])
        await consumer.commit({TopicPartition(topic=stream, partition=partition): offset})
