# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Local Classification Rules Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Django modules
from django.utils.html import escape
# NOC modules
from noc.lib.app.reportapplication import ReportApplication
from noc.fm.models.eventclassificationrule import EventClassificationRule
from noc.lib.text import indent
from noc.main.models.collectioncache import CollectionCache
from noc.core.translation import ugettext as _


class ReportClassificationRules(ReportApplication):
    title = _("Local Classification Rules (JSON)")

    def report_html(self, request, result=None, query=None):
        def is_local(r):
            return not bool(CollectionCache.objects.filter(uuid=r.uuid))

        r = ["["]
        r += [",\n".join([
            indent(r.to_json())
            for r in EventClassificationRule.objects.order_by("name")
            if is_local(r)
        ])]
        r += ["]", ""]
        return "<pre>" + escape("\n".join(r)) + "</pre>"
