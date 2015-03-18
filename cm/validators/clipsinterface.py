# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CLIPS interface validator
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from clips import CLIPSValidator


class CLIPSInterfaceValidator(CLIPSValidator):
    scope = CLIPSValidator.INTERFACE

    def get_context(self):
        ctx = super(CLIPSInterfaceValidator, self).get_context()
        mo = self.object.managed_object
        ctx.update({
            "name": mo.profile.convert_interface_name(self.object.name)
        })
        return ctx
