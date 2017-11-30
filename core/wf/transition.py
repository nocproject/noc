# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Transition Job Wrapper Class
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
# NOC modules
from noc.core.handler import get_handler
from noc.models import get_object

logger = logging.getLogger(__name__)


def transition_job(handler, model, object):
    """
    State.job_handler wrapper
    :param handler:
    :param model:
    :param object:
    :return:
    """
    # Resolve handler
    h = get_handler(handler)
    if not h:
        logger.error("Invalid handler %s", handler)
        return
    # Resolve object
    obj = get_object(model, object)
    if not obj:
        logger.error("Cannot dereference %s:%s", model, object)
    # Call handler
    h(obj)
