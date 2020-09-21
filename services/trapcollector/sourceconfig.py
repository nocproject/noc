# ----------------------------------------------------------------------
# SourceConfig
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from dataclasses import dataclass
from typing import Tuple


@dataclass
class SourceConfig(object):
    id: str
    addresses: Tuple[str, ...]
    stream: str
    partition: int
