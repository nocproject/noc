# ----------------------------------------------------------------------
# DefaultPlatformItem
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime
from typing import Optional, List

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .utils import Reference
from .label import LabelItem


class DefaultPlatformItem(BaseModel):
    id: str
    name: str
    vendor: Reference
    labels: List[LabelItem]
    effective_labels: List[LabelItem]
    full_name: Optional[str] = None
    description: Optional[str] = None
    start_of_sale: Optional[datetime.datetime] = None
    end_of_sale: Optional[datetime.datetime] = None
    end_of_support: Optional[datetime.datetime] = None
    end_of_xsupport: Optional[datetime.datetime] = None
    snmp_sysobjectid: Optional[str] = None
    aliases: Optional[List[str]] = None
    uuid: Optional[str] = None
    bi_id: Optional[str] = None


class FormPlatformItem(BaseModel):
    name: str
    vendor: Reference
    description: Optional[str] = None
    start_of_sale: Optional[datetime.datetime] = None
    end_of_sale: Optional[datetime.datetime] = None
    end_of_support: Optional[datetime.datetime] = None
    end_of_xsupport: Optional[datetime.datetime] = None
    snmp_sysobjectid: Optional[str] = None
    labels: Optional[List[str]] = None
