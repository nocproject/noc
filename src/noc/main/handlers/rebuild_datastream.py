# ---------------------------------------------------------------------
# Rebuild Datastream Handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025, The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging

# NOC modules
from noc.models import get_model
from noc.core.change.policy import change_tracker

logger = logging.getLogger(__name__)


def generate_changes(model_id):
    m = get_model(model_id)
    for r in m.objects.filter():
        change_tracker.register(
            "update",
            model_id,
            str(r.id),
            fields=[],
            datastreams=list(r.iter_changed_datastream()),
            audit=True,
        )
