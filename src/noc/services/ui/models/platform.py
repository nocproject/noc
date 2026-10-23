# ----------------------------------------------------------------------
# DefaultPlatformItem
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .utils import Reference
from .label import LabelItem


class DefaultPlatformItem(BaseModel):
    id: str
    name: str
    vendor: Reference
    labels: list[LabelItem]
    effective_labels: list[LabelItem]
    full_name: str | None = None
    description: str | None = None
    start_of_sale: datetime.datetime | None = None
    end_of_sale: datetime.datetime | None = None
    end_of_support: datetime.datetime | None = None
    end_of_xsupport: datetime.datetime | None = None
    snmp_sysobjectid: str | None = None
    aliases: list[str] | None = None
    uuid: str | None = None
    bi_id: str | None = None


class FormPlatformItem(BaseModel):
    name: str
    vendor: Reference
    description: str | None = None
    start_of_sale: datetime.datetime | None = None
    end_of_sale: datetime.datetime | None = None
    end_of_support: datetime.datetime | None = None
    end_of_xsupport: datetime.datetime | None = None
    snmp_sysobjectid: str | None = None
    labels: list[str] | None = None
