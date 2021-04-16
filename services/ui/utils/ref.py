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
from ..models.utils import Reference

TModel = TypeVar("TModel", bound=Model)
TDoc = TypeVar("TDoc", bound=Document)


def get_reference(item: Optional[Union[TModel, TDoc]]) -> Optional[Reference]:
    if not item:
        return None
    return Reference(id=str(item.id), label=str(item))
