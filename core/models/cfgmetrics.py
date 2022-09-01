# ----------------------------------------------------------------------
# Job Metric Configuration DataClass
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Literal, Tuple
from dataclasses import dataclass, field


@dataclass(frozen=True)
class MetricItem(object):
    name: str
    field_name: str = field(compare=False)
    scope_name: str = field(compare=False)
    is_stored: bool = field(compare=False, default=True)
    is_compose: bool = field(compare=False, default=False)


@dataclass(frozen=True)
class MetricCollectorConfig(object):
    collector: Literal["sla", "sensor", "managed_object"]
    #
    metrics: Tuple[MetricItem, ...]  # Metric Type List
    # Key labels
    labels: Optional[Tuple[str, ...]] = None
    # Like settings: ifindex::<ifindex>, oid::<oid>, ac::<SC/CS/S/C>
    hints: Optional[List[str]] = None
    #
    service: Optional[int] = None  # Service BI_Id
    # Collectors
    sensor: Optional[int] = None  # Sensor BI_Id
    sla_probe: Optional[int] = None  # SLA Probe BI_Id
