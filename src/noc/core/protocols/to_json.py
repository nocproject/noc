# ----------------------------------------------------------------------
# GetJsonPath protocol
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 Gufo Labs
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from pathlib import Path
from typing import Protocol


class ToJson(Protocol):
    """
    Saving to collections support.

    Must implement methods:
    - get_json_path() - relative path in colelction
    - to_json() - collection content.
    """

    def get_json_path(self) -> Path: ...
    def to_json(self) -> str: ...
