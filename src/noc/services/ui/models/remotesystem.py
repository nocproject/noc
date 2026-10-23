# ----------------------------------------------------------------------
# DefaultRemoteSystemItem
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from datetime import datetime

# Third-party modules
from pydantic import BaseModel


class EnvItem(BaseModel):
    key: str
    value: str


class DefaultRemoteSystemItem(BaseModel):
    id: str
    name: str
    handler: str
    # Environment variables
    environment: list[EnvItem]
    description: str | None = None
    # Enable extractors/loaders
    enable_admdiv: bool = False
    enable_administrativedomain: bool = False
    enable_authprofile: bool = False
    enable_container: bool = False
    enable_link: bool = False
    enable_managedobject: bool = False
    enable_managedobjectprofile: bool = False
    enable_networksegment: bool = False
    enable_networksegmentprofile: bool = False
    enable_object: bool = False
    enable_service: bool = False
    enable_serviceprofile: bool = False
    enable_subscriber: bool = False
    enable_subscriberprofile: bool = False
    enable_resourcegroup: bool = False
    enable_ttsystem: bool = False
    enable_project: bool = False
    enable_label: bool = False
    # Usage statistics
    last_extract: datetime | None = None
    last_successful_extract: datetime | None = None
    extract_error: str | None = None
    last_load: datetime | None = None
    last_successful_load: datetime | None = None
    load_error: str | None = None


class FormRemoteSystemItem(BaseModel):
    name: str
    description: str
    handler: str
    # Environment variables
    environment: list[EnvItem]
    # Enable extractors/loaders
    enable_admdiv: bool = False
    enable_administrativedomain: bool = False
    enable_authprofile: bool = False
    enable_container: bool = False
    enable_link: bool = False
    enable_managedobject: bool = False
    enable_managedobjectprofile: bool = False
    enable_networksegment: bool = False
    enable_networksegmentprofile: bool = False
    enable_object: bool = False
    enable_service: bool = False
    enable_serviceprofile: bool = False
    enable_subscriber: bool = False
    enable_subscriberprofile: bool = False
    enable_resourcegroup: bool = False
    enable_ttsystem: bool = False
    enable_project: bool = False
    enable_label: bool = False
