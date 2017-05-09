# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## RPC Wrapper
##----------------------------------------------------------------------
## Copyright (C) 2007-2017 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

_service = None


def set_service(svc):
    global _service

    _service = svc


def get_service():
    global _service

    if not _service:
        from stub import ServiceStub
        _service = ServiceStub()
        _service.start()
    return _service
