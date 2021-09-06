# ----------------------------------------------------------------------
# MetricScopeCDAGFactory
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# NOC modules
from noc.pm.models.metricscope import MetricScope
from noc.pm.models.metrictype import MetricType
from .base import BaseCDAGFactory, FactoryCtx
from ..graph import CDAG


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
    ):
        super().__init__(graph, ctx, namespace)
        self.scope = scope
        self.spool = spool
        self.sticky = sticky

    def construct(self) -> None:
        # Construct probe nodes
        probes = {}
        cleaners = {}
        for mt in MetricType.objects.filter(scope=self.scope.id).order_by("field_name"):
            name = mt.field_name
            probes[name] = self.graph.add_node(
                name,
                "probe",
                description=f"Input collector for {name} metric",
                config={
                    "unit": (mt.units.code or "1") if mt.units else "1",
                    "scale": mt.scale.code if mt.scale else "1",
                },
                sticky=self.sticky,
            )
            cleaner = mt.get_cleaner()
            if cleaner:
                cleaners[name] = cleaner
        # Construct metric sender node
        ms = self.graph.add_node(
            "sender",
            "metrics",
            description=f"{self.scope.name} metric sender",
            config={"scope": self.scope.table_name, "spool": self.spool},
            sticky=self.sticky,
        )
        # Connect to the probes
        for name, node in probes.items():
            node.subscribe(ms, name, dynamic=True)
        # Additional key fields
        for kf in self.scope.key_fields:
            ms.add_input(kf.field_name, is_key=True)
        # Set up cleaners
        for name, cleaner in cleaners.items():
            ms.set_cleaner(name, cleaner)
