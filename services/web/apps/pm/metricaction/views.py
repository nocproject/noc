# ---------------------------------------------------------------------
# pm.metricrule application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication
from noc.pm.models.metricaction import MetricAction as MA
from noc.core.translation import ugettext as _


class MetricActionInputItem(BaseModel):
    metric_type: str


class AlarmConfigItem(BaseModel):
    alarm_class: Optional[str]
    reference: Optional[str] = None
    activation_level: float = 1.0
    deactivation_level: float = 1.0
    vars: Dict[str, Any] = None
    # labels ?


class ActivationConfigItem(BaseModel):
    window_function: Optional[Literal["percentile", "nth", "expdecay", "sumstep"]] = None
    # Tick, Seconds
    window_type: Literal["tick", "seconds"] = "tick"
    window_config: Optional[Dict[str, Any]] = None
    min_window: int = 1
    max_window: int = 100
    activation_function: Optional[Literal["relu", "logistic", "indicator", "softplus"]] = None
    activation_config: Optional[Dict[str, Any]] = None


class MetricAction(BaseModel):
    inputs = List[MetricActionInputItem]
    compose_function: Literal["sum", "avg"] = None
    compose_metric_type: Optional[str] = None
    activation_config: Optional[ActivationConfigItem] = None
    deactivation_config: Optional[ActivationConfigItem] = None
    key_function: Optional[str] = None
    alarm_config: Optional[AlarmConfigItem] = None


class MetricActionApplication(ExtDocApplication):
    """
    MetricType application
    """

    title = _("Metric Action")
    menu = [_("Setup"), _("Metric Actions")]
    model = MA
    query_condition = "icontains"
    query_fields = ["name", "description"]
