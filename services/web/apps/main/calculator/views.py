# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Calculator application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator

# Third-party modules
import six

# NOC modules
from noc.lib.app.application import Application, HasPerm, view
from noc.services.web.apps.main.calculator.calculators import calculator_registry
from noc.core.translation import ugettext as _

# Register all calculators
calculator_registry.register_all()


class CalculatorApplication(Application):
    title = _("Calculators")

    @view(url=r"^$", url_name="index", menu="Calculators", access=HasPerm("view"))
    def view_index(self, request):
        r = [(cn, c.title) for cn, c in six.iteritems(calculator_registry.classes)]
        r = list(sorted(r, key=operator.itemgetter(1)))
        return self.render(request, "index.html", {"calculators": r})

    @view(url=r"^(?P<calculator>\S+)/$", url_name="calculate", access=HasPerm("view"))
    def view_calculate(self, request, calculator):
        try:
            c = calculator_registry[calculator](self)
        except KeyError:
            return self.response_not_found("No calculator found")
        return c.render(request)
