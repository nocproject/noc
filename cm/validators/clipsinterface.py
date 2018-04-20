# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# CLIPS interface validator
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
=======
##----------------------------------------------------------------------
## CLIPS interface validator
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from clips import CLIPSValidator


class CLIPSInterfaceValidator(CLIPSValidator):
    SCOPE = CLIPSValidator.INTERFACE

    def get_context(self):
        ctx = super(CLIPSInterfaceValidator, self).get_context()
        mo = self.object.managed_object
        ctx.update({
<<<<<<< HEAD
            "name": mo.get_profile().convert_interface_name(self.object.name)
=======
            "name": mo.profile.convert_interface_name(self.object.name)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        })
        return ctx
