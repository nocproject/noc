# ----------------------------------------------------------------------
# MetricScopeCDAGFactory
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Callable, Optional, Dict, List
from dataclasses import dataclass
from threading import Lock

# NOC modules
from noc.pm.models.metricscope import MetricScope
from noc.pm.models.metrictype import MetricType
from .base import BaseCDAGFactory, FactoryCtx
from ..graph import CDAG
from ..node.metrics import MetricsNodeConfig
from ..node.probe import ProbeNodeConfig


cfg_lock = Lock()


@dataclass
class ProbeConfig(object):
    name: str
    description: str
    config: ProbeNodeConfig


@dataclass
class ScopeConfig(object):
    name: str
    description: str
    config: MetricsNodeConfig
    cleaners: Dict[str, Callable]
    probes: List[ProbeConfig]
    key_fields: List[str]
    enable_timedelta: bool = False


scope_config: Dict[str, ScopeConfig] = {}


class MetricScopeCDAGFactory(BaseCDAGFactory):
    """
    Metric scope collection graph builder
    """

    def __init__(
        self,
        graph: CDAG,
        scope: MetricScope,
        ctx: Optional[FactoryCtx] = None,
        namespace: Optional[str] = None,
        spool: bool = True,
        sticky: bool = False,
        lazy_init: bool = False,
    ):
        super().__init__(graph, ctx, namespace)
        self.scope = scope
        self.spool = spool
        self.sticky = sticky
        self.lazy_init = lazy_init

    def get_scope_config(self) -> ScopeConfig:
        sc = scope_config.get(self.scope.table_name)
        if not sc:
            sc = ScopeConfig(
                name=self.scope.table_name,
                description=f"{self.scope.name} metric sender",
                config=MetricsNodeConfig(scope=self.scope.table_name, spool=self.spool),
                cleaners={},
                probes=[],
                key_fields=[kf.field_name for kf in self.scope.key_fields],
                enable_timedelta=self.scope.enable_timedelta,
            )
            for mt in MetricType.objects.filter(scope=self.scope.id).order_by("field_name"):
                name = mt.field_name
                cleaner = mt.get_cleaner()
                if cleaner:
                    sc.cleaners[name] = cleaner
                if self.lazy_init:
                    continue
                sc.probes.append(
                    ProbeConfig(
                        name=name,
                        description=f"Input collector for {name} metric",
                        config=ProbeNodeConfig(
                            unit=(mt.units.code or "1") if mt.units else "1",
                            scale=mt.scale.code if mt.scale else "1",
                        ),
                    )
                )
            scope_config[self.scope.table_name] = sc
        return sc

    def construct(self) -> None:
        # Construct probe nodes
        with cfg_lock:
            cfg = self.get_scope_config()
        # Construct metric sender node
        ms = self.graph.add_node(
            "sender",
            "metrics",
            description=cfg.description,
            config=cfg.config,
            sticky=self.sticky,
        )
        # Construct probe nodes
        for pc in cfg.probes:
            probe = self.graph.add_node(
                pc.name,
                "probe",
                description=pc.description,
                config=pc.config,
                sticky=self.sticky,
            )
            probe.subscribe(ms, pc.name, dynamic=True)
        # Set cleaners
        ms.set_scope_cleaners(cfg.name, cfg.cleaners)
        # Additional key fields
        for kf in cfg.key_fields:
            ms.add_input(kf, is_key=True)
        # Time-delta
        if cfg.enable_timedelta:
            ms.add_input("time_delta")
