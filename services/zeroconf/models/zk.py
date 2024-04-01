# ----------------------------------------------------------------------
# Zk models
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List

# Third-party modules
from pydantic import BaseModel, Field


class ZkConfigConfigZeroconf(BaseModel):
    id: Optional[int]
    key: Optional[str]
    interval: int


class ZkConfigMetrics(BaseModel):
    type: str
    url: str


class ZkConfigConfig(BaseModel):
    zeroconf: ZkConfigConfigZeroconf
    metrics: Optional[ZkConfigMetrics]


class ZkConfigCollector(BaseModel, extra="allow"):
    id: str
    type: str
    service: int
    interval: int
    labels: List[str]


class ZkConfig(BaseModel):
    version: str = Field("1", alias="$version")
    type: str = Field("zeroconf", alias="$type")
    config: ZkConfigConfig
    collectors: List[ZkConfigCollector]
