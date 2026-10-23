# ----------------------------------------------------------------------
# get_service dependency
# ----------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.service.base import BaseService
from noc.core.service.loader import get_service as _get_service


def get_service() -> BaseService:
    """
    Returns service instance
    :return:
    """
    return _get_service()
