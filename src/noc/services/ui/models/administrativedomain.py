# ----------------------------------------------------------------------
# DefaultAdministrativeDomainItem
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules

# Third-party modules
from pydantic import BaseModel

# NOC modules
from .utils import Reference
from .label import LabelItem


class DefaultAdministrativeDomainItem(BaseModel):
    id: str
    name: str
    labels: list[LabelItem]
    effective_labels: list[LabelItem]
    parent: Reference | None = None
    description: str | None = None
    default_pool: Reference | None = None
    bioseg_floating_name_template: Reference | None = None
    bioseg_floating_parent_segment: Reference | None = None
    remote_system: Reference | None = None
    remote_id: str | None = None
    bi_id: str | None = None


class FormAdministrativeDomainItem(BaseModel):
    name: str
    parent: Reference | None = None
    description: str | None = None
    default_pool: Reference | None = None
    bioseg_floating_name_template: Reference | None = None
    bioseg_floating_parent_segment: Reference | None = None
    labels: list[str] | None = None
