# ----------------------------------------------------------------------
# RedPanda client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from dataclasses import dataclass
import enum
from typing import Optional, Dict, List, AsyncIterable, Tuple, Iterator

# Third-party modules
from aiokafka.producer.producer import AIOKafkaProducer
from aiokafka.consumer.consumer import AIOKafkaConsumer, TopicPartition
from aiokafka.client import AIOKafkaClient
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import KafkaError

# NOC Modules
from noc.core.messagestream.base import (
    BaseMessageStreamClient,
    Metadata,
    PartitionMetadata,
    StreamMetadata,
    Broker,
)
from noc.core.messagestream.message import Message, PublishRequest
from noc.core.perf import metrics
from noc.config import config

logger = logging.getLogger(__name__)


class RedPandaClient(BaseMessageStreamClient):
    def __init__(self):
        super().__init__()
        self.bootstrap = config.redpanda.bootstrap_servers.split(",")
        self.producer: Optional[AIOKafkaProducer] = None
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.client: Optional[AIOKafkaClient] = None
        self.admin_client: Optional[KafkaAdminClient] = None
        self.stub = None

    async def close(self):
        """
        Close connections
        :return:
        """
        if self.producer:
            await self.producer.stop()
        # if self.admin_client:
        #    self.admin_client.close()
        # if self.client:
        #    await self.client.close()

    async def fetch_metadata(
        self, stream: Optional[str] = None, wait_for_stream: bool = False
    ) -> Metadata:
        client = await self.get_kafka_client()
        await client.bootstrap()
        r = await client.fetch_all_metadata()
        return Metadata(
            brokers=[Broker(id=b.nodeId, host=b.host, port=b.port) for b in r.brokers()],
            metadata=[
                StreamMetadata(
                    name=stream_name,
                    subject=stream_name,
                    partitions={
                        p.partition: PartitionMetadata(
                            id=p.partition,
                            leader=p.leader,
                            replicas=list(p.replicas),
                            isr=list(p.isr),
                            high_watermark=-1,
                            newest_offset=-1,
                            paused=False,
                        )
                        for p in r._partitions[stream_name].values()
                    },
                )
                for stream_name in r._partitions
            ],
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
                bootstrap_servers=self.bootstrap,
                client_id="noc",
                enable_auto_commit=False,
                group_id=group_id,
            )
        return self.consumer

    async def get_kafka_client(self) -> AIOKafkaClient:
        if not self.client:
            self.client = AIOKafkaClient(
                bootstrap_servers=self.bootstrap, client_id="noc"
            )  # config.client_id
        return self.client

    async def get_kafka_admin_client(self) -> KafkaAdminClient:
        if not self.admin_client:
            self.admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap, client_id="noc"
            )  # config.client_id
        return self.admin_client

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
        admin_client = await self.get_kafka_admin_client()
        admin_client.create_topics(
            new_topics=[NewTopic(name=name, num_partitions=partitions, replication_factor=1)],
            validate_only=False,
        )

    async def delete_stream(self, name: str) -> None:
        admin_client = await self.get_kafka_admin_client()
        admin_client.delete_topics([name])

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
        consumer = await self.get_consumer(group_id=stream)
        consumer.subscribe(topics=[stream])
        async with consumer as c:
            async for msg in c:
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
                    await c.commit(
                        {TopicPartition(msg.topic, partition=msg.partition): msg.offset + 1}
                    )
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
        logger.debug("Sending to topic %s", stream)
        producer = await self.get_producer()
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
        return 0

    async def set_cursor(self, stream: str, partition: int, cursor_id: str, offset: int) -> None:
        pass
