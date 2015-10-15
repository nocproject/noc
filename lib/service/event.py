# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Event notification settings
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## Third-party modules
import consul

logger = logging.getLogger(__name__)


def fire(topic):
    """
    Firing topic message
    """
    logger.debug("Firing on %s", topic)
    c = consul.Consul()
    c.kv.put(
        "event/%s" % topic,
        ""
    )
