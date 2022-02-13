# ----------------------------------------------------------------------
# Liftbridge client
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
from dataclasses import dataclass
import enum
from typing import Optional, Dict, List, AsyncIterable, Tuple, Iterator
import random
import asyncio
import socket

# Third-party modules
from grpc.aio import insecure_channel, AioRpcError
from grpc import StatusCode, ChannelConnectivity

# NOC modules
from noc.config import config
from noc.core.perf import metrics
from noc.core.validators import is_ipv4
from noc.core.compressor.util import get_compressor, get_decompressor
from noc.core.comp import smart_bytes
from .api_pb2_grpc import APIStub
from .api_pb2 import (
    FetchMetadataRequest,
    FetchMetadataResponse,
    FetchPartitionMetadataRequest,
    CreateStreamRequest,
    DeleteStreamRequest,
    PublishRequest,
    SubscribeRequest,
    FetchCursorRequest,
    SetCursorRequest,
    AckPolicy as _AckPolicy,
    StartPosition as _StartPosition,
    Ack,
)
from .error import (
    rpc_error,
    ErrorNotFound,
    ErrorChannelClosed,
    ErrorUnavailable,
    LiftbridgeError,
    ErrorMessageSizeExceeded,
)
from .message import Message

logger = logging.getLogger(__name__)


class AckPolicy(enum.IntEnum):
    LEADER = _AckPolicy.LEADER
    ALL = _AckPolicy.ALL
    NONE = _AckPolicy.NONE


class StartPosition(enum.IntEnum):
    NEW_ONLY = _StartPosition.NEW_ONLY  # Start at new messages after the latest
    OFFSET = _StartPosition.OFFSET  # Start at a specified offset
    EARLIEST = _StartPosition.EARLIEST  # Start at the oldest message
    LATEST = _StartPosition.LATEST  # Start at the newest message
    TIMESTAMP = _StartPosition.TIMESTAMP  # Start at a specified timestamp
    RESUME = 9999  # Non-standard -- resume from next to last processed


H_ENCODING = "X-NOC-Encoding"


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


CURSOR_STREAM = "__cursors"


class GRPCChannel(object):
    def __init__(self, broker: str):
        self.broker = broker
        self.channel = None
        self.stub = None

    def __getattr__(self, item):
        return getattr(self.stub, item)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def connect(self) -> None:
        self.channel = insecure_channel(
            self.broker,
            options=[
                ("grpc.max_send_message_length", config.liftbridge.max_message_size),
                ("grpc.max_receive_message_length", config.liftbridge.max_message_size),
                ("grpc.enable_http_proxy", config.liftbridge.enable_http_proxy),
            ],
        )
        while True:
            logger.debug("[%s] Connecting", self.broker)
            try:
                await self.wait_for_channel_ready()
            except ErrorUnavailable as e:
                logger.debug("[%s] Failed to connect: %s", self.broker, e)
                await asyncio.sleep(1)
                continue
            logger.debug("[%s] Channel is ready", self.broker)
            self.stub = APIStub(self.channel)
            return

    async def close(self) -> None:
        if not self.channel:
            return
        logger.debug("[%s] Closing channel", self.broker)
        await self.channel.close()
        self.channel = None
        self.stub = None

    async def wait_for_channel_ready(self):
        """
        Wait until channel became ready or raise ErrorUnavailable

        :param channel:
        :return:
        """
        while True:
            state = self.channel.get_state(try_to_connect=True)
            if state == ChannelConnectivity.READY:
                return
            if (
                state == ChannelConnectivity.TRANSIENT_FAILURE
                or state == ChannelConnectivity.SHUTDOWN
            ):
                raise ErrorUnavailable("Unavailable: %s" % state)
            await self.channel.wait_for_state_change(state)

    @property
    def is_connected(self) -> bool:
        return self.stub is not None


class LiftBridgeClient(object):
    GRPC_RESTARTABLE_CODES = {
        StatusCode.UNAVAILABLE,
        StatusCode.FAILED_PRECONDITION,
        StatusCode.NOT_FOUND,
        StatusCode.INTERNAL,
    }

    def __init__(self):
        self.channels: Dict[str, GRPCChannel] = {}  # broker -> GRPCChannel
        self.open_brokers: List[str] = []
        self.leaders: Dict[Tuple[str, int], str] = {}  # (stream, partition) -> broker
        self.isrs: Dict[Tuple[str, int], List[str]] = {}  # (stream, partition) -> [broker, ...]

    async def close_channel(self, broker):
        """
        Close broker channel
        :param broker:
        :return:
        """
        ch = self.channels[broker]
        await ch.close()
        del self.channels[broker]
        self.open_brokers = list(self.channels)

    async def close(self):
        """
        Close all open channels
        :return:
        """
        for broker in list(self.channels):
            await self.close_channel(broker)

    async def __aenter__(self) -> "LiftBridgeClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def get_channel(self, broker: Optional[str] = None) -> GRPCChannel:
        """
        Get GRPC channel for a broker. Use random broker from seed if broker is not set
        :param broker:
        :return:
        """
        if not broker:
            if self.channels:
                # Use random existing channel
                broker = random.choice(self.open_brokers)
            else:
                # Getting addresses from config directly will block the loop on resolve() method.
                # So get parameter via .find_parameter() and resolve explicitly.
                addresses = await config.find_parameter("liftbridge.addresses").async_get()
                # Use random broker from seed
                svc = random.choice(addresses)
                broker = "%s:%s" % (svc.host, svc.port)
        channel = self.channels.get(broker)
        if not channel:
            channel = GRPCChannel(broker)
            await channel.connect()
            self.channels[broker] = channel
            self.open_brokers = list(self.channels)
        return channel

    async def _sleep_on_error(self, delay: float = 1.0, deviation: float = 1.0):
        """
        Wait random time on error
        :return:
        """
        await asyncio.sleep(delay - deviation + 2 * deviation * random.random())

    async def get_leader(self, stream: str, partition: int) -> str:
        """
        Get leader broker for partition
        :param stream:
        :param partition:
        :return:
        """
        if not self.leaders:
            await self.__refresh_leaders()
        p_id = (stream, partition)
        while True:
            leader = self.leaders.get(p_id)
            if leader:
                return leader
            logger.debug("Leader for %s:%s is not available still. Waiting", stream, partition)
            await asyncio.sleep(1)
            await self.__refresh_leaders()

    async def get_leader_channel(self, stream: str, partition: int) -> GRPCChannel:
        """
        Get GRPCChannel for partition leader
        :param stream:
        :param partition:
        :return:
        """
        broker = await self.get_leader(stream, partition)
        return await self.get_channel(broker)

    async def __update_topology(self, r: FetchMetadataResponse) -> None:
        """
        Update partition leaders information from FetchMetadata response
        :param r:
        :return:
        """

        async def resolve(host: str):
            if is_ipv4(host):
                return host
            # Resolve from cache
            addrs = r_cache.get(host)
            if not addrs:
                # Resolve hostname
                try:
                    addr_info = await asyncio.get_running_loop().getaddrinfo(
                        host, None, proto=socket.IPPROTO_TCP
                    )
                    addrs = [x[4][0] for x in addr_info if x[0] == socket.AF_INET]
                    r_cache[host] = addrs
                except socket.gaierror as e:
                    raise ErrorNotFound("Cannot resolve broker address '%s'" % b.host) from e
            return random.choice(addrs)

        # Resolver cache
        r_cache: Dict[str, List[str]] = {}
        # Resolve brokers
        brokers: Dict[str, str] = {}  # id -> host:port
        for b in r.brokers:
            host = await resolve(b.host)
            brokers[b.id] = "%s:%s" % (host, b.port)
        # Update leaders
        self.leaders = {}
        for m in r.metadata:
            for p in m.partitions.values():
                if not p.leader:
                    logger.debug("%s:%s has no leader still", m.name, p.id)
                leader = brokers.get(p.leader)
                if not leader:
                    logger.error("%s:%s uses unknown leader broker %s", m.name, p.id, p.leader)
                    continue
                self.leaders[m.name, p.id] = leader
                self.isrs[m.name, p.id] = []
                for isr in p.isr:
                    broker = brokers.get(isr)
                    if not broker:
                        logger.error("%s:%s uses unknown isr broker %s", m.name, p.id, isr)
                        continue
                    self.isrs[m.name, p.id] += [broker]
        # Close channels for a left brokers
        for broker in set(self.channels) - set(brokers.values()):
            logger.debug("[%s] Closing left broker", broker)
            await self.close_channel(broker)

    async def __refresh_leaders(self):
        logger.info("Refresh leaders")
        await self.fetch_metadata(wait_for_stream=True)

    def __reset_leaders(self):
        self.leaders = {}

    async def fetch_metadata(
        self, stream: Optional[str] = None, wait_for_stream: bool = False
    ) -> Metadata:
        req = FetchMetadataRequest()
        if stream:
            req.streams.append(stream)
        while True:
            channel = await self.get_channel()
            r = await channel.FetchMetadata(req)
            if not r.metadata and wait_for_stream:
                await asyncio.sleep(1)
                continue
            await self.__update_topology(r)
            return Metadata(
                brokers=[Broker(id=b.id, host=b.host, port=b.port) for b in r.brokers],
                metadata=[
                    StreamMetadata(
                        name=m.name,
                        subject=m.subject,
                        partitions={
                            p.id: PartitionMetadata(
                                id=p.id,
                                leader=p.leader,
                                replicas=list(p.replicas),
                                isr=list(p.isr),
                                high_watermark=p.highWatermark,
                                newest_offset=p.newestOffset,
                                paused=p.paused,
                            )
                            for p in m.partitions.values()
                        },
                    )
                    for m in r.metadata
                ],
            )

    async def fetch_partition_metadata(
        self, stream: str, partition: int, wait_for_stream: bool = False
    ) -> PartitionMetadata:
        while True:
            channel = await self.get_leader_channel(stream, partition)
            r = await channel.FetchPartitionMetadata(
                FetchPartitionMetadataRequest(stream=stream, partition=partition)
            )
            if not r.metadata and wait_for_stream:
                await asyncio.sleep(1)
                continue
            p = r.metadata
            return PartitionMetadata(
                id=p.id,
                leader=p.leader,
                replicas=list(p.replicas),
                isr=list(p.isr),
                high_watermark=p.highWatermark,
                newest_offset=p.newestOffset,
                paused=p.paused,
            )

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
        with rpc_error():
            req = CreateStreamRequest(
                subject=subject,
                name=name,
                group=group,
                replicationFactor=replication_factor,
                partitions=partitions,
            )
            if enable_compact:
                req.compactEnabled.value = True
            else:
                req.compactEnabled.value = False
            if minisr:
                req.minIsr.value = minisr
            # Retention settings
            if retention_max_age:
                # in ms
                req.retentionMaxAge.value = retention_max_age * 1000
            if retention_max_bytes:
                req.retentionMaxBytes.value = retention_max_bytes
            # Segment settings
            if segment_max_bytes:
                req.segmentMaxBytes.value = segment_max_bytes
            if segment_max_age:
                # in ms
                req.segmentMaxAge.value = segment_max_age * 1000
            if auto_pause_time:
                req.autoPauseTime.value = auto_pause_time * 1000
                if auto_pause_disable_if_subscribers:
                    req.autoPauseDisableIfSubscribers.value = True
            channel = await self.get_channel()
            await channel.CreateStream(req)

    async def delete_stream(self, name: str) -> None:
        with rpc_error():
            channel = await self.get_channel()
            await channel.DeleteStream(DeleteStreamRequest(name=name))

    @staticmethod
    def get_publish_request(
        value: bytes,
        stream: Optional[str] = None,
        key: Optional[bytes] = None,
        partition: Optional[int] = None,
        headers: Optional[Dict[str, bytes]] = None,
        ack_inbox: Optional[str] = None,
        correlation_id: Optional[str] = None,
        ack_policy: AckPolicy = AckPolicy.LEADER,
        auto_compress: bool = False,
    ) -> PublishRequest:
        to_compress = (
            auto_compress
            and config.liftbridge.compression_method
            and config.liftbridge.compression_threshold
            and len(value) >= config.liftbridge.compression_threshold
        )
        if to_compress:
            value = get_compressor(config.liftbridge.compression_method)(value)
        # Publish Request
        req = PublishRequest(value=value, ackPolicy=ack_policy.value)
        if stream:
            req.stream = stream
        if key:
            req.key = key
        if partition:
            req.partition = partition
        if to_compress:
            req.headers[H_ENCODING] = smart_bytes(config.liftbridge.compression_method)
        if headers:
            for h, v in headers.items():
                req.headers[h] = v
        if ack_inbox:
            req.ackInbox = ack_inbox
        if correlation_id:
            req.correlationIid = correlation_id
        return req

    async def publish_sync(self, req: PublishRequest, wait_for_stream: bool = False) -> None:
        """
        Send publish request and wait for acknowledge
        :param req:
        :param wait_for_stream: Wait for stream being created.
        :return:
        """

        # Publish
        while True:
            channel = await self.get_channel()
            try:
                with rpc_error():
                    await channel.Publish(req)
                    break
            except ErrorUnavailable:
                await self.close_channel(channel.broker)
                logger.info("Loosing connection to current cluster member. Trying to reconnect")
                await asyncio.sleep(1)
            except ErrorMessageSizeExceeded as e:
                logger.error("Message size exceeded. Skipping... : %s", e)
                metrics["liftbridge_publish_size_exceeded"] += 1
                break
            except ErrorNotFound as e:
                if wait_for_stream:
                    await self.close_channel(channel.broker)
                    logger.info(
                        "Stream '%s' is not available yet. Maybe election in progress. "
                        "Trying to reconnect",
                        req.stream,
                    )
                    await asyncio.sleep(1)
                else:
                    raise ErrorNotFound(str(e)) from e  # Reraise

    async def publish_async(
        self, iter_req: Iterator[PublishRequest], wait: bool = True
    ) -> AsyncIterable[Ack]:
        async def drain_wait():
            nonlocal balance, done
            for req in iter_req:
                balance += 1
                yield req
            done = asyncio.Event()
            await asyncio.wait_for(done.wait(), config.liftbridge.publish_async_ack_timeout)

        balance: int = 0
        done: Optional[asyncio.Event] = None
        with rpc_error():
            channel = await self.get_channel()
            async for ack in channel.PublishAsync(drain_wait() if wait else iter_req):
                balance -= 1
                if done is not None and not balance:
                    done.set()
                yield ack

    async def publish(
        self,
        value: bytes,
        stream: Optional[str] = None,
        key: Optional[bytes] = None,
        partition: Optional[int] = None,
        headers: Optional[Dict[str, bytes]] = None,
        ack_inbox: Optional[str] = None,
        correlation_id: Optional[str] = None,
        ack_policy: AckPolicy = AckPolicy.LEADER,
        wait_for_stream: bool = False,
        auto_compress: bool = False,
    ) -> None:
        # Build message
        req = self.get_publish_request(
            value,
            stream=stream,
            key=key,
            partition=partition,
            headers=headers,
            ack_inbox=ack_inbox,
            correlation_id=correlation_id,
            ack_policy=ack_policy,
            auto_compress=auto_compress,
        )
        # Publish
        await self.publish_sync(req, wait_for_stream=wait_for_stream)

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
        # Build request
        req = SubscribeRequest(stream=stream)
        to_restore_position = start_position == StartPosition.RESUME
        if partition:
            req.partition = partition
        if resume:
            req.resume = resume
        if allow_isr:
            req.readISRReplica = True
        if start_offset is not None:
            req.startPosition = StartPosition.OFFSET
            req.startOffset = start_offset
        elif start_timestamp is not None:
            req.startPosition = StartPosition.TIMESTAMP
            req.startTimestamp = int(start_timestamp * 1_000_000_000.0)
        elif start_position == StartPosition.RESUME:
            if not cursor_id:
                raise ValueError("cursor_id must be set for StartPosition.RESUME")
            logger.debug("Getting stored offset for stream '%s'" % stream)
            req.startPosition = StartPosition.OFFSET
            logger.debug("Resuming from offset %d", req.startOffset)
        else:
            req.startPosition = start_position
        to_recover: bool = False  # Recover flag. Set if clint from LiftbridgeError recover
        last_offset: Optional[int] = None
        while True:
            try:
                async for msg in self._subscribe(
                    req,
                    restore_position=to_restore_position,
                    cursor_id=cursor_id,
                    to_recover=to_recover,
                ):
                    yield msg
                    last_offset = msg.offset
            except ErrorUnavailable as e:
                logger.error("Subscriber looses connection to partition node: %s", e)
                logger.info("Reconnecting")
                self.__reset_leaders()
                await self._sleep_on_error()
                if not to_restore_position and last_offset is not None:
                    # Continue from last seen position
                    req.startPosition = StartPosition.OFFSET
                    req.startOffset = last_offset + 1
                    to_restore_position = False
            except LiftbridgeError as e:
                logger.error("Subscriber channel was unknown error: %s", e)
                logger.info("Try to continue from last offset")
                if not to_restore_position and last_offset is not None:
                    # Continue from last seen position
                    req.startPosition = StartPosition.OFFSET
                    req.startOffset = last_offset + 1
                    to_restore_position = False
                    to_recover = True
                # For cluster problem recommended 30 second wait
                await self._sleep_on_error(delay=30, deviation=10)

    async def _subscribe(
        self,
        req: SubscribeRequest,
        restore_position: bool = False,
        cursor_id: Optional[str] = None,
        to_recover: bool = False,
    ) -> AsyncIterable[Message]:
        allow_isr = bool(req.readISRReplica)
        with rpc_error():
            broker: Optional[str] = None
            if allow_isr:
                isrs = self.isrs.get((req.stream, req.partition))
                if isrs:
                    broker = random.choice(isrs)
            if not broker:
                broker = await self.get_leader(req.stream, req.partition)
            async with GRPCChannel(broker) as channel:
                logger.debug("[%s] Subscribing stream '%s'", broker, req.stream)
                if restore_position and cursor_id:
                    req.startOffset = await self.fetch_cursor(
                        stream=req.stream, partition=req.partition, cursor_id=cursor_id
                    )
                if req.startOffset:
                    logger.debug("[%s] Resuming from position %d", broker, req.startOffset)
                call = channel.Subscribe(req)
                # NB: We cannot use `async for msg in call` construction
                # Due to liftbridge protocol specific:
                # --- CUT ---
                # When the subscription stream is created, the server sends an empty message
                # to indicate the subscription was successfully created. Otherwise, an error
                # is sent on the stream if the subscribe failed. This handshake message
                # must be handled and should not be exposed to the user.
                # --- CUT ---
                # So grpc aio implementation treats first message as aio.EOF
                # and hangs forever trying to get error status from core.
                # So we use own inlined `_fetch_stream_responses` implementation here
                msg = await call._read()
                logger.debug("[%s] Stream is ready, waiting for messages", broker)
                # Next, process all other messages
                msg = await call._read()
                to_recover = False  # clean if message successful get
                while msg:
                    value = msg.value
                    headers = msg.headers
                    if H_ENCODING in headers:
                        comp = headers.pop(H_ENCODING).decode()
                        value = get_decompressor(comp)(value)
                    yield Message(
                        value=value,
                        subject=msg.subject,
                        offset=msg.offset,
                        timestamp=msg.timestamp,
                        key=msg.key,
                        partition=msg.partition,
                        headers=headers,
                    )
                    msg = await call._read()
                # Get core message to explain the result
                code = await call.code()
                detail = await call.debug_error_string()
                if code in self.GRPC_RESTARTABLE_CODES:
                    raise ErrorUnavailable()
                if code == StatusCode.UNKNOWN and not to_recover:
                    raise LiftbridgeError(str(detail))
                raise ErrorChannelClosed(str(code))

    async def fetch_cursor(self, stream: str, partition: int, cursor_id: str) -> int:
        with rpc_error():
            while True:
                channel = await self.get_leader_channel(CURSOR_STREAM, 0)
                try:
                    r = await channel.FetchCursor(
                        FetchCursorRequest(stream=stream, partition=partition, cursorId=cursor_id)
                    )
                except AioRpcError as e:
                    logger.info("Failed to get cursor: %s", e)
                    if e.code() in self.GRPC_RESTARTABLE_CODES:
                        self.__reset_leaders()
                        await self._sleep_on_error()
                        continue
                    raise e
                v = r.offset or 0
                logger.debug(
                    "Fetching cursor %s for %s:%s: current value is %s",
                    cursor_id,
                    stream,
                    partition,
                    v,
                )
                return v

    async def set_cursor(self, stream: str, partition: int, cursor_id: str, offset: int) -> None:
        with rpc_error():
            while True:
                try:
                    channel = await self.get_leader_channel(CURSOR_STREAM, 0)
                    await channel.SetCursor(
                        SetCursorRequest(
                            stream=stream,
                            partition=partition,
                            cursorId=cursor_id,
                            offset=offset + 1,
                        )
                    )
                    return
                except AioRpcError as e:
                    logger.info("Failed to set cursor: %s", e)
                    if e.code() in self.GRPC_RESTARTABLE_CODES:
                        self.__reset_leaders()
                        await self._sleep_on_error()
                        continue
                    raise e
