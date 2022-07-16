# ----------------------------------------------------------------------
# @change Models
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Any
from dataclasses import dataclass


@dataclass(frozen=True)
class ChangeField(object):
    field: str  # FieldName
    new: Any  # New Value
    old: Optional[Any] = None  # Old Value
