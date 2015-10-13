# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Event notification settings
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import json
import logging
## Third-party modules
import tornadoredis
## NOC modules
from noc import settings

logger = logging.getLogger(__name__)

_client = None

def send(topic, message=None):
    global _client
    if not _client:
        logger.info("Connecting to redis server %s",
                    settings.REDIS_HOST)
        _client = tornadoredis.Client(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT
        )
        _client.connect()
    message = message or {}
    if not isinstance(message, basestring):
        message = json.dumps(message)
    logger.debug("Sending message to %s: %s", topic, message)
    _client.publish(topic, message)
