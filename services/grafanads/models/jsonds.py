# ----------------------------------------------------------------------
# Json GrafanaDS models
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import List, Optional, Dict, Any, Union

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
    panel_id: int = Field(..., alias="panelId")
    range: RangeSection
    range_raw: Optional[Dict[str, str]] = Field(None, alias="rangeRaw")
    interval: str = "30s"
    interval_ms: int = Field(30_000, alias="intervalMs")
    max_datapoints: int = Field(500, alias="maxDataPoints")
    targets: List[TargetItem]
    adhoc_filters: Optional[List[AdhocFilterItem]] = Field(None, alias="adhocFilters")
    result_type: str = Field("timeseries", alias="format")  # matrix


class TargetResponseItem(BaseModel):
    target: str
    datapoints: List[List[float]]


class SearchResponseItem(BaseModel):
    text: str
    value: str


# Search
class SearchRequset(BaseModel):
    target: str


# Variable
class VariableRequest(BaseModel):
    payload: Dict[str, Any]
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
