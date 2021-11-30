# ----------------------------------------------------------------------
# Pydentic models for grafanads service
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pydantic import BaseModel, Field


class RangeSingle(BaseModel):
    from_: str = Field(..., alias="from")
    to: str


class RangeSection(BaseModel):
    from_: str = Field(..., alias="from")
    to: str
    raw: RangeSingle


class AnnotationSection(BaseModel):
    name: str
    datasource: str
    enable: bool
    icon_color: str = Field(..., alias="iconColor")
    query: str


class Annotation(BaseModel):
    range: RangeSection
    annotation: AnnotationSection
    range_raw: RangeSingle = Field(..., alias="rangeRaw")
