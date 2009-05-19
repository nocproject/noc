# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Syntax hilighting utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import pygments.formatters.html
from pygments.formatters import HtmlFormatter
from django.utils.html import escape

##
## HTML Formatter
## Returns escaped HTML text with neat line numbers
##
class NOCHtmlFormatter(HtmlFormatter):
    name = 'NOC HTML'
    
    def __init__(self,**kwargs):
        kwargs["linenos"]="inline"
        super(NOCHtmlFormatter,self).__init__(**kwargs)
