# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# AnyConstraint
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .base import BaseConstraint


class AnyConstraint(BaseConstraint):
    """
    Always true
    """

    def __and__(self, other):
        # type: (BaseConstraint) -> BaseConstraint
        return other

    def __or__(self, other):
        # type: (BaseConstraint) -> BaseConstraint
        return other
