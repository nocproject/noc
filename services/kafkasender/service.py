#!./bin/python
# ----------------------------------------------------------------------
# kafkasender service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# Third-party modules
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

# NOC modules
from noc.config import config
from noc.core.service.fastapi import FastAPIService
from noc.core.perf import metrics
from noc.core.liftbridge.message import Message
from noc.core.mx import MX_TO, MX_SHARDING_KEY
from noc.core.comp import smart_text


KAFKASENDER_STREAM = "kafkasender"


class KafkaSenderService(FastAPIService):
    name = "kafkasender"

    def __init__(self):
        super().__init__()
        self.producer: Optional[AIOKafkaProducer] = None

    async def on_activate(self):
        self.slot_number, self.total_slots = await self.acquire_slot()
        await self.subscribe_stream(KAFKASENDER_STREAM, self.slot_number, self.on_message)

    async def on_message(self, msg: Message) -> None:
        """
        Process incoming message. Usually forwarded by `mx` service.
        Message MUST have `To` header, containing target Kafka topic.

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
        await self.send_to_kafka(smart_text(dst), msg.value, msg.headers.get(MX_SHARDING_KEY))
        metrics["messages_processed"] += 1

    async def send_to_kafka(self, topic: str, data: bytes, key: Optional[bytes] = None) -> None:
        """
        Send data to kafka topic

        :param topic:
        :param data:
        :return:
        """
        self.logger.debug("Sending to topic %s", topic)
        producer = await self.get_producer()
        try:
            await producer.send_and_wait(topic, data, key=key)
            metrics["messages_sent_ok", topic] += 1
            metrics["bytes_sent", topic] += len(data)
        except KafkaError as e:
            metrics["messages_sent_error", topic] += 1
            self.logger.error("Failed to send to topic %s: %s", topic, e)

    async def get_producer(self) -> AIOKafkaProducer:
        """
        Returns connected kafka producer
        :return:
        """
        if not self.producer:
            bootstrap = [x.strip() for x in config.kafkasender.bootstrap_servers.split(",")]
            self.logger.info("Connecting to producer using bootstrap services %s", bootstrap)
            self.producer = AIOKafkaProducer(
                bootstrap_servers=bootstrap,
                acks="all",
                sasl_mechanism=config.kafkasender.sasl_mechanism,
                security_protocol=config.kafkasender.security_protocol,
                sasl_plain_username=config.kafkasender.username,
                sasl_plain_password=config.kafkasender.password,
            )
            await self.producer.start()
        return self.producer


if __name__ == "__main__":
    KafkaSenderService().start()
