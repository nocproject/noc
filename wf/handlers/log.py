# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## LogHandler
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import logging
# Django modules
from django.template import Template, Context
# NOC modules
from base import BaseHandler
from noc.sa.interfaces.base import StringParameter


class LogHandler(BaseHandler):
    """
    Log message
    """
    params = {
        "format": StringParameter()
    }

    def handler(self, process, node, format=""):
        s = Template(format).render(process.context)
        logging.info(s)
