# ----------------------------------------------------------------------
# Model utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional

# Third-party modules
from pydantic import BaseModel


class Reference(BaseModel):
    id: str
    label: Optional[str]
