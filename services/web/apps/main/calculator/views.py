# ---------------------------------------------------------------------
# Calculator application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator

# NOC modules
from noc.services.web.base.application import Application, HasPerm, view
from noc.core.translation import ugettext as _
from .calculators.loader import loader


class CalculatorApplication(Application):
    title = _("Calculators")

    @view(url=r"^$", url_name="index", menu="Calculators", access=HasPerm("view"))
    def view_index(self, request):
        r = [(cn, loader[cn].title) for cn in loader]
        r = sorted(r, key=operator.itemgetter(1))
        return self.render(request, "index.html", {"calculators": r})

    @view(url=r"^(?P<calculator>\S+)/$", url_name="calculate", access=HasPerm("view"))
    def view_calculate(self, request, calculator):
        try:
            c = loader[calculator](self)
        except KeyError:
            return self.response_not_found("No calculator found")
        return c.render(request)
