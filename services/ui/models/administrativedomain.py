# ----------------------------------------------------------------------
# DefaultAdministrativeDomainItem
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, List

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .utils import Reference
from .label import LabelItem


class DefaultAdministrativeDomainItem(BaseModel):
    id: str
    name: str
    labels: List[LabelItem]
    effective_labels: List[LabelItem]
    parent: Optional[Reference] = None
    description: Optional[str] = None
    default_pool: Optional[Reference] = None
    bioseg_floating_name_template: Optional[Reference] = None
    bioseg_floating_parent_segment: Optional[Reference] = None
    remote_system: Optional[Reference] = None
    remote_id: Optional[str] = None
    bi_id: Optional[str] = None


class FormAdministrativeDomainItem(BaseModel):
    name: str
    parent: Optional[Reference] = None
    description: Optional[str] = None
    default_pool: Optional[Reference] = None
    bioseg_floating_name_template: Optional[Reference] = None
    bioseg_floating_parent_segment: Optional[Reference] = None
    labels: Optional[List[str]] = None
