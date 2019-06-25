# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Various django hacks
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.apps import apps
# NOC modules
from noc.models import get_model


def ensure_pending_models():
    """
    Django's ForeignKey with string rel resolves when
    appropriate model class being imported.

    :return:
    """
    for app, model in apps._pending_lookups:
        get_model("%s.%s" % (app, model))  # Ensure model loading
