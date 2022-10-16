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


@dataclass(frozen=True)
class RetentionPolicy(object):
    retention_bytes: int = 0
    segment_bytes: int = 0
    retention_ages: int = 86400
    segment_ages: int = 3600


@dataclass(frozen=True)
class StreamConfig(object):
    name: Optional[str] = None  #
    shard: Optional[str] = None  #
    partitions: Optional[int] = None  # Partition numbers
    slot: Optional[str] = None  # Configured slots
    cursor: Optional[str] = None  # Cursor name
    enable: bool = True  # Stream is active
    auto_pause_time: bool = False
    auto_pause_disable: bool = False
    replication_factor: Optional[int] = None
    retention_policy: RetentionPolicy = RetentionPolicy()

    def get_partitions(self) -> int:
        from noc.core.service.loader import get_service

        if self.partitions is not None:
            return self.partitions

        # Slot-based streams
        svc = get_service()
        return svc.get_slot_limits(f"{self.slot}-{self.shard}" if self.shard else self.slot)

    @property
    def cursor_name(self) -> Optional[str]:
        return self.cursor or self.slot

    @property
    def stream_name(self):
        if self.shard:
            return f"{self.name}.{self.shard}"
        return self.name

    def __str__(self):
        return self.name


STREAM_CONFIG: Dict[str, StreamConfig] = {
    "events": StreamConfig(
        slot="classifier",
        retention_policy=RetentionPolicy(
            retention_bytes=config.liftbridge.stream_events_retention_max_bytes,
            retention_ages=config.liftbridge.stream_events_retention_max_age,
            segment_bytes=config.liftbridge.stream_events_segment_max_bytes,
            segment_ages=config.liftbridge.stream_events_segment_max_age,
        ),
    ),
    "dispose": StreamConfig(
        slot="correlator",
        retention_policy=RetentionPolicy(
            retention_bytes=config.liftbridge.stream_dispose_retention_max_bytes,
            retention_ages=config.liftbridge.stream_dispose_retention_max_age,
            segment_bytes=config.liftbridge.stream_dispose_segment_max_bytes,
            segment_ages=config.liftbridge.stream_dispose_segment_max_age,
        ),
    ),
    "message": StreamConfig(
        slot="mx",
        retention_policy=RetentionPolicy(
            retention_bytes=config.liftbridge.stream_message_retention_max_bytes,
            retention_ages=config.liftbridge.stream_message_retention_max_age,
            segment_bytes=config.liftbridge.stream_message_segment_max_bytes,
            segment_ages=config.liftbridge.stream_message_retention_max_age,
        ),
    ),
    "revokedtokens": StreamConfig(partitions=1),
    "jobs": StreamConfig(
        slot="worker",
        retention_policy=RetentionPolicy(
            retention_bytes=config.liftbridge.stream_jobs_retention_max_bytes,
            retention_ages=config.liftbridge.stream_jobs_retention_max_age,
            segment_bytes=config.liftbridge.stream_jobs_segment_max_bytes,
            segment_ages=config.liftbridge.stream_jobs_segment_max_age,
        ),
    ),
    "metrics": StreamConfig(
        slot="metrics",
        replication_factor=1,
        retention_policy=RetentionPolicy(
            retention_bytes=config.liftbridge.stream_metrics_retention_max_bytes,
            retention_ages=config.liftbridge.stream_metrics_retention_max_age,
            segment_bytes=config.liftbridge.stream_metrics_segment_max_bytes,
            segment_ages=config.liftbridge.stream_metrics_segment_max_age,
        ),
    ),
    "ch": StreamConfig(
        partitions=len(config.clickhouse.cluster_topology.split(",")),
        slot=None,
        replication_factor=1,
        retention_policy=RetentionPolicy(
            retention_bytes=config.liftbridge.stream_ch_retention_max_bytes,
            retention_ages=config.liftbridge.stream_ch_retention_max_age,
            segment_bytes=config.liftbridge.stream_ch_segment_max_bytes,
            segment_ages=config.liftbridge.stream_ch_segment_max_age,
        ),
    ),
    # Sender
    "tgsender": StreamConfig(name="tgsender", slot="tgsender"),
    "icqsender": StreamConfig(name="icqsender", slot="icqsender"),
    "mailsender": StreamConfig(name="mailsender", slot="mailsender"),
    "kafkasender": StreamConfig(name="kafkasender", slot="kafkasender"),
}

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

    @staticmethod
    async def _sleep_on_error(delay: float = 1.0, deviation: float = 1.0):
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
            try:
                r: FetchMetadataResponse = await channel.FetchMetadata(req)
            except AioRpcError as e:
                logger.info("Failed to get metadata: %s", e)
                if e.code() in self.GRPC_RESTARTABLE_CODES:
                    await self._sleep_on_error(delay=10)
                    continue
                raise e
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

    async def _create_stream(
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

    @classmethod
    def get_stream_config(cls, name: str) -> StreamConfig:
        cfg_name, *shard = name.split(".", 1)
        base_cfg = None
        if cfg_name in STREAM_CONFIG:
            base_cfg = STREAM_CONFIG[cfg_name]
        return StreamConfig(
            name=name,
            shard=shard[0] if shard else None,
            partitions=base_cfg.partitions if base_cfg else None,
            retention_policy=base_cfg.retention_policy if base_cfg else RetentionPolicy(),
        )

    async def create_stream(
        self,
        name: str,
        subject: str,
        group: Optional[str] = None,
        partitions: int = 0,
        replication_factor: int = 0,
    ) -> None:
        cfg = self.get_stream_config(name)
        minisr = 0
        if cfg.replication_factor:
            replication_factor = min(cfg.replication_factor, replication_factor)
            minisr = min(2, replication_factor)
        await self._create_stream(
            subject=subject,
            name=name,
            partitions=partitions or cfg.get_partitions(),
            minisr=minisr,
            replication_factor=replication_factor,
            retention_max_bytes=cfg.retention_policy.retention_bytes,
            retention_max_age=cfg.retention_policy.retention_ages,
            segment_max_bytes=cfg.retention_policy.segment_bytes,
            segment_max_age=cfg.retention_policy.segment_ages,
            auto_pause_time=cfg.auto_pause_time,
            auto_pause_disable_if_subscribers=cfg.auto_pause_disable,
        )

    async def delete_stream(self, name: str) -> None:
        with rpc_error():
            channel = await self.get_channel()
            await channel.DeleteStream(DeleteStreamRequest(name=name))

    async def alter_stream(
        self, current_meta: StreamMetadata, new_partitions: int, replication_factor: int
    ) -> bool:
        name = current_meta.name
        old_partitions = len(current_meta.partitions)
        n_msg: Dict[int, int] = {}  # partition -> copied messages

        logger.info(f"Altering stream %s", name)
        # Create temporary stream with same structure, as original one
        tmp_stream = f"__tmp-{name}"
        logger.info(f"Creating temporary stream %s", tmp_stream)
        await self.create_stream(
            subject=tmp_stream,
            name=tmp_stream,
            partitions=old_partitions,
            replication_factor=replication_factor,
        )
        # Copy all unread data to temporary stream as is
        for partition in range(old_partitions):
            logger.info("Copying partition %s:%s to %s:%s", name, partition, tmp_stream, partition)
            n_msg[partition] = 0
            # Get current offset
            p_meta = await self.fetch_partition_metadata(name, partition)
            newest_offset = p_meta.newest_offset or 0
            # Fetch cursor
            current_offset = await self.fetch_cursor(
                stream=name,
                partition=partition,
                # cursor_id=stream.cursor_name,
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
        await self.create_stream(
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
                logger.info(f"  %s messages restored", n_msg[partition])
            else:
                logger.info("  nothing to restore")
        # Drop temporary stream
        logger.info(f"Dropping temporary stream %s", tmp_stream)
        await self.delete_stream(tmp_stream)
        # Uh-oh
        logger.info(f"Stream %s has been altered", name)
        return True

    async def ensure_stream(self, name: str, partitions: Optional[int] = None) -> bool:
        """
        Ensure stream settings
        :param name:
        :return:
        """
        cfg = self.get_stream_config(name)
        meta = await self.fetch_metadata(name)
        rf = min(len(meta.brokers), 2)
        stream_meta = meta.metadata[0]
        # Check if stream is configured properly
        if stream_meta and len(stream_meta.partitions) == cfg.partitions:
            return False
        elif stream_meta:
            # Alter settings
            logger.info(
                "Altering stream %s due to partition/replication factor mismatch (%d -> %d)",
                name,
                len(stream_meta.partitions),
                cfg.partitions,
            )
            return await self.alter_stream(meta, cfg.partitions)
        logger.info(f"Creating stream %s with %s partitions", name, cfg.partitions)
        await self.create_stream(name, subject=name, replication_factor=rf)
        return True

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
                        "Stream '%s/%s' is not available yet. Maybe election in progress. "
                        "Trying to reconnect to: %s:%s",
                        req.stream,
                        req.partition,
                        channel.broker,
                        channel,
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
