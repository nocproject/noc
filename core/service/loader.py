# ----------------------------------------------------------------------
# Service loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

_service = None


def set_service(svc):
    global _service

    _service = svc


def get_service():
    global _service

    if not _service:
        from noc.core.ioloop.util import setup_asyncio
        from .stub import ServiceStub

        setup_asyncio()
        _service = ServiceStub()
        _service.start()
    return _service


def get_dcs():
    return get_service().dcs
