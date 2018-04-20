# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Syntax hilighting utilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2009 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
=======
##----------------------------------------------------------------------
## Syntax hilighting utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
"""
"""
import pygments.formatters.html
from pygments.formatters import HtmlFormatter
from django.utils.html import escape

<<<<<<< HEAD
#
# HTML Formatter
# Returns escaped HTML text with neat line numbers
#
class NOCHtmlFormatter(HtmlFormatter):
    name = 'NOC HTML'

=======
##
## HTML Formatter
## Returns escaped HTML text with neat line numbers
##
class NOCHtmlFormatter(HtmlFormatter):
    name = 'NOC HTML'
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def __init__(self,**kwargs):
        kwargs["linenos"]="table"
        super(NOCHtmlFormatter,self).__init__(**kwargs)
