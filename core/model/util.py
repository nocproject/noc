# ----------------------------------------------------------------------
# Various model utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db.models import Field


def is_related_field(f: Field) -> bool:
    """
    Check field instance is related field.

    :param f:
    :return:
    """
    return f.remote_field is not None
