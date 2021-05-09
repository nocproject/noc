# ----------------------------------------------------------------------
# DefaultRemoteSystemItem
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List
from datetime import datetime

# Third-party modules
from pydantic import BaseModel


class EnvItem(BaseModel):
    key: str
    value: str


class DefaultRemoteSystemItem(BaseModel):
    id: str
    name: str
    description: Optional[str]
    handler: str
    # Environment variables
    environment: List[EnvItem]
    # Enable extractors/loaders
    enable_admdiv: bool
    enable_administrativedomain: bool
    enable_authprofile: bool
    enable_container: bool
    enable_link: bool
    enable_managedobject: bool
    enable_managedobjectprofile: bool
    enable_networksegment: bool
    enable_networksegmentprofile: bool
    enable_object: bool
    enable_service: bool
    enable_serviceprofile: bool
    enable_subscriber: bool
    enable_subscriberprofile: bool
    enable_resourcegroup: bool
    enable_ttsystem: bool
    enable_project: bool
    enable_label: bool
    # Usage statistics
    last_extract: Optional[datetime]
    last_successful_extract: Optional[datetime]
    extract_error: Optional[str]
    last_load: Optional[datetime]
    last_successful_load: Optional[datetime]
    load_error: Optional[str]


class FormRemoteSystemItem(BaseModel):
    name: str
    description: str
    handler: str
    # Environment variables
    environment: List[EnvItem]
    # Enable extractors/loaders
    enable_admdiv: bool
    enable_administrativedomain: bool
    enable_authprofile: bool
    enable_container: bool
    enable_link: bool
    enable_managedobject: bool
    enable_managedobjectprofile: bool
    enable_networksegment: bool
    enable_networksegmentprofile: bool
    enable_object: bool
    enable_service: bool
    enable_serviceprofile: bool
    enable_subscriber: bool
    enable_subscriberprofile: bool
    enable_resourcegroup: bool
    enable_ttsystem: bool
    enable_project: bool
    enable_label: bool
