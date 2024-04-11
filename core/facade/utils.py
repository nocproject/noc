# ---------------------------------------------------------------------
# Facade utilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

rx_id = re.compile("[^a-z-A-Z0-9]")
PLACEHOLDER = "-"


def name_to_id(name: str) -> str:
    """
    Convert name to valid id.
    """
    parts = [rx_id.sub(PLACEHOLDER, x.strip()).lower() for x in name.split("|")]
    return f"noc-{PLACEHOLDER.join(parts)}"


def name_to_title(name: str) -> str:
    """
    Use last part of name as title.
    """
    return name.split("|")[-1].strip()


def slot_to_id(name: str) -> str:
    """
    Convert slot name to id.
    """
    s = rx_id.sub(PLACEHOLDER, name).lower()
    return f"noc-slot-{s}"
