# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# CLIPS subinterface validator
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .clipsinterface import CLIPSInterfaceValidator


class CLIPSSubInterfaceValidator(CLIPSInterfaceValidator):
    SCOPE = CLIPSInterfaceValidator.SUBINTERFACE
