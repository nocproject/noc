# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Service loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

_service = None


def set_service(svc):
    global _service

    if _service:
        print "@@@@ STUB SERVICE IS ALREADY ACTIVATED"
    _service = svc


def get_service():
    global _service

    if not _service:
        from .stub import ServiceStub
        _service = ServiceStub()
        _service.start()
    return _service


def get_dcs():
    return get_service().dcs
