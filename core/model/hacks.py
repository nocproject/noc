# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Various django hacks
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.db.models.fields.related import pending_lookups
# NOC modules
from noc.models import get_model


def ensure_pending_models():
    """
    Django's ForeignKey with string rel resolves when
    appropriate model class being imported.


    :return:
    """
    for m in list(pending_lookups):
        get_model(".".join(m))  # Ensure model loading
