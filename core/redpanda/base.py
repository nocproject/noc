# ----------------------------------------------------------------------
# RedPanda client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from dataclasses import dataclass
import asyncio
from typing import Optional, Dict, AsyncIterable

# Third-party modules
from aiokafka.producer.producer import AIOKafkaProducer
from aiokafka.consumer.consumer import AIOKafkaConsumer, TopicPartition
from aiokafka.structs import OffsetAndTimestamp
from aiokafka.client import AIOKafkaClient
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import KafkaError, UnknownTopicOrPartitionError

# NOC Modules
from noc.core.perf import metrics
from noc.config import config
from noc.core.liftbridge.base import StartPosition
from noc.core.models.cfgmessagestreams import (
    get_stream_config,
    StreamMetadata,
    Metadata,
    PartitionMetadata,
    Broker,
)

logger = logging.getLogger(__name__)

CLIENT_ID = "NOC"


@dataclass
class Message(object):
    value: bytes
    subject: str
    offset: int
    timestamp: int
    key: bytes
    partition: int
    headers: Dict[str, bytes]


@dataclass(frozen=True)
class PublishRequest(object):
    __slots__ = ("stream", "message", "partition", "key", "headers", "auto_compress")
    stream: str
    message: bytes
    partition: int
    key: bytes
    headers: Optional[Dict[str, bytes]]
    auto_compress: bool


class RedPandaClient(object):
    TIMESTAMP_MULTIPLIER = TS_NS = 1_000

    def __init__(self):
        super().__init__()
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
        r = await client.fetch_all_metadata()
        metadata = {}
        req_parts = []
        for m_stream in r._partitions:
            if stream and stream != m_stream:
                continue
            metadata[m_stream] = StreamMetadata(name=m_stream, subject=m_stream, partitions={})
            for p in r._partitions[m_stream].values():
                req_parts.append(TopicPartition(topic=m_stream, partition=p.partition))
                metadata[m_stream].partitions[p.partition] = PartitionMetadata(
                    id=p.partition,
                    leader=p.leader,
                    replicas=list(p.replicas),
                    isr=list(p.isr),
                    high_watermark=-1,
                    newest_offset=-1,
                    paused=False,
                )
        # Fetch newest offset
        con = await self.get_consumer()
        # await con.start()
        offsets = await con.end_offsets(req_parts)
        for tp, offset in offsets.items():
            metadata[tp.topic].partitions[tp.partition].newest_offset = offset
            metadata[tp.topic].partitions[tp.partition].high_watermark = offset
        return Metadata(
            brokers=[Broker(id=b.nodeId, host=b.host, port=b.port) for b in r.brokers()],
            metadata=list(metadata.values()),
        )

    async def fetch_partition_metadata(
        self, stream: str, partition: int, wait_for_stream: bool = False
    ) -> PartitionMetadata:
        """
        Fetch Partition metadata
        :param stream:
        :param partition:
        :param wait_for_stream:
        :return:
        """
        con = await self.get_consumer()
        tp = TopicPartition(topic=stream, partition=partition)
        logger.info("Fetch partition metadata: %s/%s", stream, partition)
        con.assign([tp])
        ef = await con.end_offsets([tp])
        meta = con._client.cluster._partitions[stream][partition]
        # Lookup broker address
        brokers = {b.nodeId: f"{b.host}:{b.port}" for b in con._client.cluster.brokers()}
        return PartitionMetadata(
            id=partition,
            leader=meta.leader,
            replicas=[brokers[hid] for hid in meta.replicas],
            isr=[brokers[hid] for hid in meta.isr],
            # high_watermark=con.highwater(tp),
            # newest_offset=con.last_stable_offset(tp),
            high_watermark=ef[tp],
            newest_offset=ef[tp],
            paused=False,
        )

    async def get_producer(self) -> AIOKafkaProducer:
        """
        Returns connected kafka producer
        :return:
        """
        if not self.producer:
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
            await self.producer.start()
        return self.producer

    async def get_consumer(self, group_id=None) -> AIOKafkaConsumer:
        if not self.consumer:
            self.consumer = AIOKafkaConsumer(
                loop=self.loop,
                bootstrap_servers=self.bootstrap,
                client_id=CLIENT_ID,
                enable_auto_commit=False,
                group_id=group_id,
            )
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
        cfg = get_stream_config(name)
        r = {}
        if cfg.retention_policy.retention_bytes:
            r["retention.bytes"] = str(cfg.retention_policy.retention_bytes)
        if cfg.retention_policy.retention_ages:
            r["retention.ms"] = str(cfg.retention_policy.retention_ages * 1000)
        if cfg.retention_policy.segment_bytes:
            r["segment.bytes"] = str(cfg.retention_policy.segment_bytes)
        if cfg.retention_policy.segment_ages:
            r["segment.ms"] = str(cfg.retention_policy.segment_ages * 1000)
        # "min.insync.replicas": 2,
        return r or None

    async def create_stream(
        self,
        name: str,
        subject: str,
        group: Optional[str] = None,
        partitions: int = 0,
        replication_factor: int = 0,
    ) -> None:
        """
        Create Stream by settings
        :param name:
        :param subject:
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
        start_position: StartPosition = StartPosition.NEW_ONLY,
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
        #     bootstrap_servers='10.36.129.20:9092,10.36.129.19:9092,10.36.129.21:9092'
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
        :param start_position:
        :param start_offset: Offset for staring read
        :param start_timestamp: Timestamp for staring read
        :param resume:
        :param cursor_id:
        :param timeout:
        :param allow_isr:
        :return:
        """
        consumer = await self.get_consumer()
        to_restore_position = start_position == StartPosition.RESUME
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
        elif to_restore_position:
            logger.debug("Getting stored offset for stream '%s'", stream)
            r = await consumer.seek_to_committed(tp)
            logger.debug("Resuming from offset %d", r[tp])
        else:
            await consumer.seek_to_end(*tp)
        # async with consumer as c:
        async for msg in consumer:
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
        auto_compress: bool = False,
        **kwargs,
    ) -> None:
        """
        Publish message to stream
        :param value:
        :param stream:
        :param key:
        :param partition:
        :param headers:
        :param auto_compress:
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
        await self.publish(req.message, req.stream, req.key, req.partition, req.headers)

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

    async def ensure_stream(self, name: str, partitions: Optional[int] = None) -> bool:
        """
        Ensure stream settings
        :param name:
        :param partitions:
        :return:
        """
        # Get stream config
        cfg = get_stream_config(name)
        # Get liftbridge metadata
        partitions = partitions or cfg.get_partitions()
        # Check if stream is configured properly
        if not partitions:
            logger.info("Stream '%s' without partition. Skipping..", name)
            return False
        meta = await self.fetch_metadata(name)
        rf = min(len(meta.brokers), 2)
        stream_meta = meta.metadata[0] if meta.metadata else None
        if stream_meta and len(stream_meta.partitions) == partitions:
            return False
        elif stream_meta and stream_meta.partitions:
            # Alter settings
            logger.info(
                "Altering stream %s due to partition/replication factor mismatch (%d -> %d)",
                name,
                len(stream_meta.partitions),
                partitions,
            )
            # return await self.alter_stream(
            #     stream_meta, new_partitions=partitions, replication_factor=rf
            # )
        logger.info("Creating stream %s with %s partitions", name, partitions)
        await self.create_stream(name, partitions=partitions, subject=name, replication_factor=rf)
        return True
