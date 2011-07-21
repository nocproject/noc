# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Local Classification Rules Report
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.utils.html import escape
## NOC modules
from noc.lib.app.reportapplication import ReportApplication
from noc.fm.models import EventClassificationRule
from noc.lib.text import indent

class ReportClassificationRules(ReportApplication):
    title = "Local Classification Rules (JSON)"
    
    def report_html(self):
        r = ["["]
        r += [",\n".join([indent(r.to_json())
                          for r in EventClassificationRule.objects.filter(is_builtin=False)])]
        r += ["]",""]
        return "<pre>" + escape("\n".join(r)) + "</pre>"
