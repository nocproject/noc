# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# DCS utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import sys
# Third-party modules
import tornado.ioloop
import tornado.gen
import six
# NOC modules
from .loader import get_dcs_url, get_dcs_class


def resolve(name, hint=None, wait=True, timeout=None,
            full_result=False):
    """
    Returns *hint* when service is active or new service
    instance,
    :param name:
    :param hint:
    :param wait:
    :param timeout:
    :param full_result:
    :return:
    """
    @tornado.gen.coroutine
    def _resolve():
        try:
            r = yield dcs.resolve(
                name, hint=hint, wait=wait,
                timeout=timeout,
                full_result=full_result
            )
            result.append(r)
        except tornado.gen.Return as e:
            result.append(e.value)
        except Exception:
            error.append(sys.exc_info())

    url = get_dcs_url()
    io_loop = tornado.ioloop.IOLoop()
    result = []
    error = []
    dcs = get_dcs_class()(url, ioloop=io_loop)
    io_loop.run_sync(_resolve)
    if error:
        six.reraise(*error[0])
    else:
        return result[0]
