# ---------------------------------------------------------------------
# dBm to mW conversion
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django import forms

# NOC modules
from noc.core.convert.dbm import dbm2mw, mw2dbm
from .base import BaseCalculator


class CalculatorForm(forms.Form):
    value = forms.DecimalField(required=True)
    measure = forms.ChoiceField(required=True, choices=[("dbm", "dBm"), ("mw", "mW")])


class Calculator(BaseCalculator):
    name = "dbm2mw"
    title = "dBm to mW"
    form_class = CalculatorForm

    def calculate(self, value, measure):
        if measure == "dbm":
            r = [("dBm", value), ("mW", dbm2mw(value))]
        else:  # mW
            r = [("dBm", mw2dbm(value)), ("mW", value)]
        return r
