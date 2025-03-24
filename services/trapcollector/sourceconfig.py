# ----------------------------------------------------------------------
# SourceConfig
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Tuple, Optional, List


@dataclass
class RemoteSystemData(object):
    id: str
    name: str


@dataclass
class AdministrativeDomainData(object):
    id: int
    name: str
    remote_system: Optional[RemoteSystemData] = None


@dataclass
class ManagedObjectData(object):
    id: str
    name: str
    administrative_domain: AdministrativeDomainData
    bi_id: int = None
    labels: List[str] = None
    remote_system: Optional[RemoteSystemData] = None
    remote_id: Optional[str] = None


@dataclass
class SourceConfig(object):
    id: str
    addresses: Tuple[str, ...]
    stream: str
    partition: int
    bi_id: Optional[int] = None
    name: Optional[str] = None
    sa_profile: Optional[str] = None
    effective_labels: List[str] = None
    managed_object: Optional[ManagedObjectData] = None
    storm_policy: str = "D"
    storm_threshold: int = 1000
