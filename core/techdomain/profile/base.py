# ----------------------------------------------------------------------
# BaseProfileController
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import logging

# NOC modules
from noc.core.log import PrefixLoggerAdapter


class BaseProfileController(object):
    """
    Base class for profile controller.

    Must implement `setup()` and `cleanup()` methods.

    Profile controllers must be placed in
    `sa/profiles/<vendor>/<name>/controller/<tech_domain>.py`
    and implement ProfileController class derived
    from this one.
    """

    name: str

    def __init__(self):
        self.logger = PrefixLoggerAdapter(logging.getLogger("controller"), self.name)
