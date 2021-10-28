# ---------------------------------------------------------------------
# Dispose Request
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Union

# NOC modules
from .clearreq import ClearRequest
from .eventreq import EventRequest
from .raisereq import RaiseRequest

DisposeRequest = Union[ClearRequest, EventRequest, RaiseRequest]
