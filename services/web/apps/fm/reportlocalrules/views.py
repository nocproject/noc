# ---------------------------------------------------------------------
# Local Classification Rules Report
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.utils.html import escape

# NOC modules
from noc.services.web.base.reportapplication import ReportApplication
from noc.fm.models.eventclassificationrule import EventClassificationRule
from noc.core.text import indent
from noc.core.translation import ugettext as _
from noc.core.collection.base import Collection
from noc.core.comp import smart_text


class ReportClassificationRules(ReportApplication):
    title = _("Local Classification Rules (JSON)")

    def report_html(self, request, result=None, query=None):
        builtins = Collection.get_builtins("fm.eventclassificationrules")
        b_data = [
            indent(rr.to_json())
            for rr in EventClassificationRule.objects.order_by("name")
            if rr.uuid and smart_text(rr.uuid) not in builtins
        ]
        if not b_data:
            return "<pre>" + _("No local rules") + "</pre>"
        r = ["[", ",\n".join(b_data), "]", ""]
        return "<pre>" + escape("\n".join(r)) + "</pre>"
