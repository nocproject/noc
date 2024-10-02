#!./bin/python
# ----------------------------------------------------------------------
# kafkasender service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Union, List
from collections import defaultdict

# Third-party modules
from aiokafka import AIOKafkaProducer
from aiokafka.errors import (
    KafkaError,
    KafkaConnectionError,
    KafkaTimeoutError,
    RequestTimedOutError,
)
from kafka.errors import NodeNotReadyError
from atomicl import AtomicLong

# NOC modules
from noc.config import config
from noc.core.service.fastapi import FastAPIService
from noc.core.perf import metrics
from noc.core.msgstream.message import Message
from noc.core.mx import MX_TO, MX_SHARDING_KEY, KAFKA_PARTITION
from noc.core.comp import smart_text
from noc.core.timeout import retry_timeout


KAFKASENDER_STREAM = "kafkasender"


class KafkaSenderService(FastAPIService):
    name = "kafkasender"
    use_telemetry = True
    number_message = defaultdict(lambda: AtomicLong(-1))

    def __init__(self):
        super().__init__()
        self.producer: Optional[AIOKafkaProducer] = None

    async def on_activate(self):
        self.slot_number, self.total_slots = await self.acquire_slot()
        await self.subscribe_stream(
            KAFKASENDER_STREAM, self.slot_number, self.on_message, async_cursor=True
        )

    async def on_message(self, msg: Message) -> None:
        """
        Process incoming message. Usually forwarded by `mx` service.
        Message MUST have `To` header, containing target Kafka topic.
        Optional parameter 'Kafka_partition' can be specified.

        :param msg:
        :return:
        """
        metrics["messages"] += 1
        self.logger.debug("[%d] Receiving message %s", msg.offset, msg.headers)
        dst = msg.headers.get(MX_TO)
        if not dst:
            self.logger.debug("[%d] Missed '%s' header. Dropping", msg.offset, MX_TO)
            metrics["messages_drops"] += 1
            return
        await self.send_to_kafka(
            smart_text(dst),
            msg.value,
            msg.headers.get(MX_SHARDING_KEY),
            self.get_partition(msg.headers.get(KAFKA_PARTITION), msg.headers.get(MX_TO)),
        )
        metrics["messages_processed"] += 1

    async def send_to_kafka(
        self, topic: str, data: bytes, key: Optional[bytes] = None, partition: Optional[int] = None
    ) -> None:
        """
        Send data to kafka topic

        :param topic:
        :param data:
        :param key:
        :param partition:
        :return:
        """
        self.logger.debug("Sending to topic %s, partition: %s", topic, partition)
        producer = await self.get_producer()
        if partition is not None:
            partition = int(partition)
        try:
            await producer.send(topic, data, key=key, partition=partition)
            metrics["messages_sent_ok", ("topic", topic)] += 1
            metrics["bytes_sent", ("topic", topic)] += len(data)
        except (RequestTimedOutError, AttributeError) as e:
            # Internal error
            metrics["messages_sent_error", ("topic", topic)] += 1
            self.logger.error("Fatal error when send message: %s", e)
            await self.producer.stop()
            self.producer = None
        except KafkaTimeoutError:
            metrics["messages_kafka_timeout_error", ("topic", topic)] += 1
            self.logger.error("Produce timeout... maybe we want to resend data again?")
        except KafkaError as e:
            metrics["messages_sent_error", ("topic", topic)] += 1
            self.logger.error("Failed to send to topic %s: %s", topic, e)

    async def get_producer(self) -> AIOKafkaProducer:
        """
        Returns connected kafka producer
        :return:
        """
        if self.producer:
            return self.producer
        bootstrap = [x.strip() for x in config.kafkasender.bootstrap_servers.split(",")]
        self.logger.info("Connecting to producer using bootstrap services %s", bootstrap)
        self.producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap,
            acks=1,
            max_batch_size=config.kafkasender.max_batch_size,
            sasl_mechanism=config.kafkasender.sasl_mechanism,
            security_protocol=config.kafkasender.security_protocol,
            sasl_plain_username=config.kafkasender.username,
            sasl_plain_password=config.kafkasender.password,
            retry_backoff_ms=10000,
        )
        while True:
            try:
                self.logger.info("Try starting producer")
                await self.producer.start()
                break
            except (KafkaConnectionError, NodeNotReadyError) as e:
                # KafkaConnectionError: No connection to node with id 1
                metrics["errors", ("type", "kafka_producer_start")] += 1
                self.logger.error("Failed to connect producer: %s", e)
            await retry_timeout(10.0, name="kafka_producer")
        return self.producer

    @classmethod
    def get_partition(cls, partitions: Union[bytes, List], topic: bytes) -> Union[bytes, None]:
        """
        Get partitions from headers kafka.

        Args:
            partitions: bytes. Example: 0,1,2
            topic: Topic for Kafka
        """
        if partitions is None:
            return None
        elif isinstance(partitions, bytes):
            partitions = [partition.strip() for partition in partitions.decode("utf-8").split(",")]

        if len(partitions) == 1:
            return partitions[0].encode("utf-8")
        cls.number_message[topic] += 1
        return partitions[cls.number_message[topic].value % len(partitions)].encode("utf-8")


if __name__ == "__main__":
    KafkaSenderService().start()
