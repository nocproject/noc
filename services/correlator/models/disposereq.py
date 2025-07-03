# ---------------------------------------------------------------------
# Dispose Request
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from typing import Union

# NOC modules
from .clearreq import ClearRequest
from .clearidreq import ClearIdRequest
from .eventreq import EventRequest
from .raisereq import RaiseRequest
from .ensuregroupreq import EnsureGroupRequest
from .setstatusreq import SetStatusRequest
from .raiserefreq import RaiseReferenceRequest

DisposeRequest = Union[
    ClearRequest,
    ClearIdRequest,
    EventRequest,
    RaiseRequest,
    EnsureGroupRequest,
    SetStatusRequest,
    RaiseReferenceRequest,
]
