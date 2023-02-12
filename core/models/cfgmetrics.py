# ----------------------------------------------------------------------
# Job Metric Configuration DataClass
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List, Literal, Tuple, Dict, Union
from dataclasses import dataclass, field


@dataclass(frozen=True)
class MetricItem(object):
    name: str
    field_name: str = field(compare=False)
    scope_name: str = field(compare=False)
    is_stored: bool = field(compare=False, default=True)
    is_compose: bool = field(compare=False, default=False)
    interval: int = field(compare=False, default=300)

    def get_effective_collected_interval(self, collected_interval: int):
        """
        Calculated Effective collected interval
        :param collected_interval:
        :return:
        """
        return collected_interval * max(1, round(self.interval / collected_interval))


@dataclass(frozen=True)
class MetricCollectorConfig(object):
    collector: Literal["sla", "sensor", "managed_object", "cpe"]
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
    cpe: Optional[int] = None

    def get_hints(self) -> Dict[str, Union[str, int]]:
        if not self.hints:
            return {}
        return dict(v.split("::", 1) for v in self.hints)

    def get_source_code(self, interval: int):
        """
        Get Source Code for metric
        :param interval: Metric Collected Interval
        :return:
        """
        if self.collector == "sla":
            return f"sla:{self.sla_probe}:{interval}"
        elif self.collector == "sensor":
            return f"sensor:{self.sensor}:{interval}"
        elif self.collector == "cpe":
            return f"cpe:{self.cpe}:{interval}"
        return f"managed_object:{','.join(self.labels or [])}:{interval}"
