# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Config parsing basevalidator
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## Django modules
from django.template import Template, Context
## NOC modules
from base import BaseValidator

logger = logging.getLogger(__name__)


class TextValidator(BaseValidator):
    SCOPE = BaseValidator.OBJECT | BaseValidator.INTERFACE

    def expand_template(self, tpl, context=None):
        return Template(tpl).render(Context(context or {}))

    def get_config_block(self):
        if self.scope == self.INTERFACE:
            return self.engine.get_interface_config(self.object.name)
        else:
            return self.engine.config
