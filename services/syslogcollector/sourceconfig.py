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
    bi_id: int
    process_events: bool
    archive_events: bool
    stream: str
    partition: int
