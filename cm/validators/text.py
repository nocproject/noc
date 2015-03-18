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
    scope = BaseValidator.OBJECT

    def expand_template(self, tpl, context=None):
        return Template(tpl).render(Context(context or {}))
