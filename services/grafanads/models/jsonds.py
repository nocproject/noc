# ----------------------------------------------------------------------
# Json GrafanaDS models
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import List, Optional, Dict, Any, Union, Tuple, Literal

# Third-party modules
from pydantic import BaseModel, Field


class RangeSingle(BaseModel):
    from_: Union[datetime.datetime, str] = Field(..., alias="from")
    to: Union[datetime.datetime, str]


class RangeSection(BaseModel):
    from_: datetime.datetime = Field(..., alias="from")
    to: datetime.datetime
    raw: RangeSingle


class DataSourceItem(BaseModel):
    type_: str = Field(..., alias="type")
    uid: str


# Annotations
class AnnotationSection(BaseModel):
    name: str
    datasource: Union[str, DataSourceItem]
    enable: bool
    icon_color: str = Field(..., alias="iconColor")
    query: str


class AnnotationRequest(BaseModel):
    range: RangeSection
    annotation: AnnotationSection
    range_raw: RangeSingle = Field(..., alias="rangeRaw")


class Annotation(BaseModel):
    title: str
    time: int
    annotation: AnnotationSection


# Query
class AdhocFilterItem(BaseModel):
    key: str
    value: str
    operator: str = "="


class TargetItem(BaseModel):
    target: str
    ref_id: str = Field("A", alias="refId")
    datasource: Optional[Union[str, DataSourceItem]] = None
    payload: Optional[Dict[str, Any]] = None


class QueryRequest(BaseModel):
    # string when query on Explorer
    panel_id: Union[int, str] = Field(..., alias="panelId")
    range: RangeSection
    range_raw: Optional[Dict[str, str]] = Field(None, alias="rangeRaw")
    request_id: Optional[str] = Field(None, alias="requestId")
    timezone: Optional[str] = None
    # When query on Explorer
    app: Optional[str] = None
    interval: str = "30s"
    interval_ms: int = Field(30_000, alias="intervalMs")
    max_datapoints: int = Field(500, alias="maxDataPoints")
    targets: List[TargetItem]
    adhoc_filters: Optional[List[AdhocFilterItem]] = Field(None, alias="adhocFilters")
    result_type: str = Field("time_series", alias="format")  # matrix


class TargetResponseItem(BaseModel):
    target: str
    datapoints: List[Tuple[float, int]]


class SearchResponseItem(BaseModel):
    text: str
    value: str


# Search
class SearchRequset(BaseModel):
    target: str


class PayloadSelectOptionItem(BaseModel):
    value: str
    label: Optional[str] = None  # The label of the payload select option.


class MetricPayload(BaseModel):
    label: str
    name: str
    #  If the value is select, the UI of the payload is a radio box.
    #  If the value is multi-select, the UI of the payload is a multi selection box;
    #  if the value is input, the UI of the payload is an input box;
    #  if the value is textarea, the UI of the payload is a multiline input box. The default is input.
    type: Literal["select", "multi-select", "textarea", "input"] = "input"
    placeholder: str = ""  # Input box / selection box prompt information.
    reload_metric: bool = Field(
        False, alias="reloadMetric"
    )  # Whether to overload the metrics API after modifying the value of the payload.
    width: int = 10  # Set the input / selection box width to a multiple of 8px.
    options: Optional[List[PayloadSelectOptionItem]] = None


class MetricsResponseItem(BaseModel):
    value: str
    label: Optional[str] = None
    payloads: Optional[List[MetricPayload]] = None


# Metrics
class MetricsPayloadRequest(BaseModel):
    payload: Optional[Dict[str, Any]]


# Metric Payload Options
class MetricPayloadOptionsRequest(BaseModel):
    metric: str  # Current metric
    name: str  # The payload name of the option list needs to be obtained.
    payload: Optional[Dict[str, Any]] = None  # Current payload


class VariableRequestTarget(BaseModel):
    target: Any


# Variable
class VariableRequest(BaseModel):
    payload: VariableRequestTarget
    range: RangeSection = None


class VariableItem(BaseModel):
    text: str = Field(..., alias="__text")
    value: str = Field(..., alias="__value")


class TagKeyItem(BaseModel):
    type_: Optional[str] = Field(..., alias="type")
    text: str


class TagValueQuery(BaseModel):
    key: str


class TagValueItem(BaseModel):
    text: str


# Example

"""
{
  "panelId": 1,
  "range": {
    "from": "2016-10-31T06:33:44.866Z",
    "to": "2016-10-31T12:33:44.866Z",
    "raw": {
      "from": "now-6h",
      "to": "now"
    }
  },
  "rangeRaw": {
    "from": "now-6h",
    "to": "now"
  },
  "interval": "30s",
  "intervalMs": 30000,
  "maxDataPoints": 550,
  "targets": [
     { "target": "Packets", "refId": "A", "payload": { "additional": "optional json" } },
     { "target": "Errors", "refId": "B" }
  ],
  "adhocFilters": [{
    "key": "City",
    "operator": "=",
    "value": "Berlin"
  }]
}
"""
