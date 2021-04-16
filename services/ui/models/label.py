# ----------------------------------------------------------------------
# LabelItem
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from pydantic import BaseModel


class LabelItem(BaseModel):
    id: str
    label: str
