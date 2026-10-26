# ---------------------------------------------------------------------
# Calculator application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.core.translation import ugettext as _
from noc.services.web.base.application import Application, HasPerm, api, view

from .calculators.base import calculator_loader


class CalculatorApplication(Application):
    title = _("Calculators")

    @api.get(r"^$", url_name="index", menu="Calculators", access=HasPerm("view"))
    def api_index(self, request: HttpRequest):
        r = [(cn, calculator_loader.get(cn).title) for cn in calculator_loader]
        r = sorted(r, key=operator.itemgetter(1))
        return self.render(request, "index.html", {"calculators": r})

    @view(url=r"^(?P<calculator>\S+)/$", url_name="calculate", access=HasPerm("view"))
    def view_calculate(self, request: HttpRequest, calculator):
        try:
            c = calculator_loader.get(calculator)(self)
        except KeyError:
            return self.response_not_found("No calculator found")
        return c.render(request)
