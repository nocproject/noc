# ----------------------------------------------------------------------
# Zk models
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import List

# Third-party modules
from pydantic import BaseModel, Field, Extra


class ZkConfigConfigZeroconf(BaseModel):
    id: int
    key: str
    interval: int


class ZkConfigConfig(BaseModel):
    zeroconf: ZkConfigConfigZeroconf


class ZkConfigCollector(BaseModel):
    class Config:
        extra = Extra.allow  # Allow additional configuration attributes

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
