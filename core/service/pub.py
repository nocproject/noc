#!./bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# NSQ Publish API
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging
# Third-party modules
import ujson
import pycurl


logger = logging.getLogger(__name__)

NSQD_URL = "http://127.0.0.1:4151/"
NSQD_PUB_URL = NSQD_URL + "pub"
NSQD_MPUB_URL = NSQD_URL + "mpub"


def _post(url, body):
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.POST, 1)
    c.setopt(c.POSTFIELDS, body)
    c.setopt(c.NOPROXY, "*")
    # c.setopt(c.RESOLVE, ["%s:%s" % (l, l.split(":")[0])])
    c.setopt(c.TIMEOUT, 60)
    c.setopt(c.CONNECTTIMEOUT, 10)
    try:
        c.perform()
    except pycurl.error as e:
        raise Exception(str(e))
    finally:
        c.close()


def pub(topic, data):
    logger.debug("Publish to topic %s", topic)
    data = ujson.dumps(data)
    _post(
        "%s?topic=%s" % (NSQD_PUB_URL, topic),
        data
    )
