# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# peer.PeeringPoint tests
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .base import BaseModelTest
from noc.peer.models.peeringpoint import PeeringPoint


class TestTestPeerPeeringPoint(BaseModelTest):
    model = PeeringPoint
