# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# CLIPS interface validator
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
# NOC modules
from .clips import CLIPSValidator


class CLIPSObjectValidator(CLIPSValidator):
    SCOPE = CLIPSValidator.OBJECT
