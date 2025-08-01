# ---------------------------------------------------------------------
# PathInfo embedded model
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Union, Tuple
from enum import Enum

# Third-party modules
from mongoengine.document import EmbeddedDocument
from mongoengine.fields import EnumField, ListField, StringField

# NOC modules
from noc.core.feature import Feature

HAS_FGALARMS = Feature.FGALARMS.is_active()
HAS_CHANNEL = Feature.CHANNEL.is_active()


def _is_required_index(x: Union[str, Tuple[str, ...]]) -> bool:
    """Check if index is allowed by feature gates."""
    if isinstance(x, tuple) and sum(1 for v in x if "resource_path." in v) == 2:
        return HAS_FGALARMS
    return True


class PathCode(Enum):
    """
    Code for PathItem.

    Arguments:
        OBJECT: Object.
        CHANNEL: Channel.
        ADM_DOMAIN: Administrative domain.
        SEGMENT: Network Segmwent.
    """

    OBJECT = "o"
    CHANNEL = "c"
    ADM_DOMAIN = "a"
    SEGMENT = "s"


class PathItem(EmbeddedDocument):
    meta = {"strict": False}

    code = EnumField(PathCode, required=True, db_field="c")
    path = ListField(StringField(), required=True, db_field="p")

    def __str__(self) -> str:
        return f"{self.code.value}: {self.path!s}"
