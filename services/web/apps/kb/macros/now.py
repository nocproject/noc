# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# now macro
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import datetime
# Third-party modules
from django.utils.dateformat import DateFormat
# NOC modules
from .base import BaseMacro


class Macro(BaseMacro):
    """
    now macro
    Returns current date and time
    Optional arguments
        format - PHP date()-like format string
    """
    name = "now"

    @classmethod
    def handle(cls, args, text):
        if "format" in args:
            format_string = args["format"]
        else:
            format_string = "Y.m.d H:i:s"
        df = DateFormat(datetime.datetime.now())
        return df.format(format_string)
