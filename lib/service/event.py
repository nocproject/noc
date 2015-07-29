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
import requests

NSQ_HTTP_ADDRESS = "127.0.0.1:4151"
logger = logging.getLogger(__name__)


def send(name, pool=None, data=None):
    """
    Send event notification to NSQ system
    """
    data = data or {}
    if not isinstance(data, basestring):
        data = json.dumps(data)
    topic = "ev.%s" % name
    if pool:
        topic += ".%s" % pool
    topic += "%23ephemeral"
    url = "http://%s/put?topic=%s" % (NSQ_HTTP_ADDRESS, topic)
    logger.debug("Event: %s" % topic)
    r = requests.post(url, data)
    if r.status_code != 200:
        logger.error("Failed to send event: %s", r.text)
