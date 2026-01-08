# ----------------------------------------------------------------------
# Write channel service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import asyncio
import logging
from collections import defaultdict
from time import perf_counter
from typing import Optional, Set, Dict, Tuple, List, FrozenSet, Iterable, DefaultDict

# NOC modules
from noc.services.metricscollector.sourceconfig import RemoteSystemConfig


class RemoteSystemChannel(object):
    def __init__(
        self,
        service,
        remote_system: RemoteSystemConfig,
        collector: str,
        batch_delay: Optional[int] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.service = service
        self.collector = collector
        self.remote_system: RemoteSystemConfig = remote_system
        self.logger = logger
        self.last_offset: int = 0
        # Data for deduplicate input key: Ts, Host, Labels
        self.data: DefaultDict[Tuple[int, str, FrozenSet[str]], Dict[str, float]] = defaultdict(
            dict
        )
        self.sensors_data: Dict[Tuple[int, str], float] = {}
        self.size: int = 0
        self.records: int = 0
        self.deduplicated: int = 0
        self.expired: Optional[float] = None
        self.feed_ready = asyncio.Event()
        self.feed_ready.set()
        self.flush_unknown_metrics = False
        self.flush_unknown_hosts = False
        self.unknown_metrics: Set[str] = set()
        self.unknown_hosts: Set[str] = set()
        self.last_received_hosts: Dict[str, int] = {}
        self.min_batch_size = remote_system.batch_size
        if batch_delay:
            self.ttl = float(batch_delay)
        else:
            self.ttl = float(remote_system.batch_delay_s)

    @property
    def is_banned(self) -> bool:
        return False

    async def feed(
        self,
        target: str,
        metric: str,
        values: List[Tuple[int, float]],
        labels: Optional[Iterable[str]] = None,
        sensor_id: Optional[str] = None,
    ):
        """Feed the message. Returns optional offset of last saved message"""
        if target in self.unknown_hosts:
            return
        # Wait until feed became possible
        await self.feed_ready.wait()
        # Resolve Target, Resolve Metric, Filter Labels
        cfg = self.service.lookup_source_by_name(
            target,
            collector=self.collector,
        )  # receiver
        if not cfg:
            self.unknown_hosts.add(target)
            return
        if cfg.no_data_check and values:
            self.last_received_hosts[cfg.id] = values[0][0]
        # if metric in self.unknown_metrics:
        #     return
        # Try sensor
        if sensor_id:
            sensor_cfg = self.service.lookup_remote_sensor(sensor_id, self.remote_system.name)
        else:
            sensor_cfg = None
        # Parse Labels for metrics
        cfg_metric = self.service.get_cfg_metric(self.collector, metric, labels=labels)
        if not cfg_metric:
            # Key Labels
            self.unknown_metrics.add(metric)
        if not sensor_id and not cfg_metric:
            return
        # Append data
        for v in values:
            # if ((v[0], cfg.id, frozenset(labels or [])) in self.data
            #         and cfg_metric.id in self.data[(v[0], cfg.id, frozenset(labels or []))]):
            #     self.deduplicated += 1
            if cfg_metric:
                key = (v[0], cfg.id, frozenset(labels or []))
                self.data[key][cfg_metric.id] = v[1]
            if sensor_cfg:
                self.sensors_data[(v[0], sensor_cfg.id)] = v[1]
            self.size += len(str(v))
            self.records += 1
            self.last_offset = max(self.last_offset, v[0])
        if not self.expired:
            self.expired = perf_counter() + self.ttl
        if self.is_ready_to_flush():
            await self.schedule_flush()
            await self.feed_ready.wait()

    def is_expired(self, ts: float) -> bool:
        """Check if channel is expired to given timestamp"""
        return self.expired and self.expired < ts

    def is_ready_to_flush(self) -> bool:
        """Check if channel is ready to flush"""
        if not self.size:
            return False
        return self.records >= self.min_batch_size

    async def schedule_flush(self):
        if not self.feed_ready.is_set():
            return  # Already scheduled
        self.expired = None
        self.feed_ready.clear()
        await self.service.flush_queue.put(self)

    def flush_complete(self):
        """Called when data are safely flushed"""
        self.data = defaultdict(dict)
        self.sensors_data = {}
        self.size = 0
        self.records = 0
        self.expired = None
        if self.flush_unknown_metrics:
            self.unknown_metrics = set()
            self.flush_unknown_metrics = False
            self.logger.info(
                "[%s] Clean unknown metrics: %s", self.remote_system.name, len(self.unknown_metrics)
            )
        if self.flush_unknown_hosts:
            self.unknown_hosts = set()
            self.flush_unknown_hosts = False
            self.logger.info(
                "[%s] Clean unknown Hosts: %s", self.remote_system.name, len(self.unknown_hosts)
            )
        self.feed_ready.set()
