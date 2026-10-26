# ---------------------------------------------------------------------
# Dispose Request
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules

from .clearidreq import ClearIdRequest
from .clearreq import ClearRequest
from .dispositionreq import DispositionRequest
from .ensuregroupreq import EnsureGroupRequest
from .eventreq import EventRequest
from .raisereq import RaiseRequest
from .setstatusreq import SetStatusRequest

DisposeRequest = (
    ClearRequest
    | ClearIdRequest
    | EventRequest
    | RaiseRequest
    | EnsureGroupRequest
    | SetStatusRequest
    | DispositionRequest
)
