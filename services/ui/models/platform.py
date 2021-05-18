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
    full_name: Optional[str]
    description: Optional[str]
    vendor: Reference
    start_of_sale: Optional[datetime.datetime]
    end_of_sale: Optional[datetime.datetime]
    end_of_support: Optional[datetime.datetime]
    end_of_xsupport: Optional[datetime.datetime]
    snmp_sysobjectid: Optional[datetime.datetime]
    aliases: Optional[List[str]]
    labels: List[LabelItem]
    uuid: Optional[str]
    effective_labels: List[LabelItem]
    bi_id: Optional[str]


class FormPlatformItem(BaseModel):
    name: str
    vendor: Reference
    description: Optional[str]
    start_of_sale: Optional[datetime.datetime]
    end_of_sale: Optional[datetime.datetime]
    end_of_support: Optional[datetime.datetime]
    end_of_xsupport: Optional[datetime.datetime]
    snmp_sysobjectid: Optional[datetime.datetime]
    labels: Optional[List[str]]
