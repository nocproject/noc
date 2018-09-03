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


class CLIPSInterfaceValidator(CLIPSValidator):
    SCOPE = CLIPSValidator.INTERFACE

    def get_context(self):
        ctx = super(CLIPSInterfaceValidator, self).get_context()
        mo = self.object.managed_object
        ctx.update({
            "name": mo.get_profile().convert_interface_name(self.object.name)
        })
        return ctx
