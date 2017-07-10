# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# now macro
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
import datetime

from django.utils.dateformat import DateFormat

from noc.services.web.apps.kb.parsers.macros import Macro as MacroBase


#
# now macro
#     Returns current date and time
#     Optional arguments
#     format - PHP date()-like format string
#
#
class Macro(MacroBase):
    name = "now"
    @classmethod
    def handle(cls, args, text):
        if "format" in args:
            format_string = args["format"]
        else:
            format_string = "Y.m.d H:i:s"
        df = DateFormat(datetime.datetime.now())
        return df.format(format_string)
