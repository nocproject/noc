# ----------------------------------------------------------------------
# get_reference
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Union, TypeVar

# Third-party modules
from django.db.models import Model
from mongoengine.document import Document

# NOC modules
from noc.main.models.label import Label
from noc.inv.models.resourcegroup import ResourceGroup
from ..models.utils import Reference
from ..models.label import LabelItem


TModel = TypeVar("TModel", bound=Model)
TDoc = TypeVar("TDoc", bound=Document)


def get_reference(item: Optional[Union[TModel, TDoc]]) -> Optional[Reference]:
    if not item:
        return None
    return Reference(id=str(item.id), label=str(item))


def get_reference_label(item: "Label") -> Optional[LabelItem]:
    if not item:
        return None
    return LabelItem(
        id=str(item.id),
        name=str(item.name),
        is_protected=item.is_protected,
        scope=item.name.rsplit("::", 1)[0] if item.is_scoped else "",
        value=item.name.split("::")[-1],
        bg_color1=f"#{item.bg_color1:06x}",
        fg_color1=f"#{item.fg_color1:06x}",
        bg_color2=f"#{item.bg_color2:06x}",
        fg_color2=f"#{item.fg_color2:06x}",
    )


def get_reference_rg(item: "ResourceGroup") -> Optional[Reference]:
    if not item:
        return None
    rg = ResourceGroup.get_by_id(item)
    return Reference(id=str(rg.id), label=str(rg))
