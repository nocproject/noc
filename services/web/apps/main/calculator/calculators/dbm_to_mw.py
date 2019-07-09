# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# dBm to mW conversion
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django import forms

# NOC modules
from noc.services.web.apps.main.calculator.calculators import Calculator as CalculatorBase
from noc.lib.convert import dbm2mw, mw2dbm


class CalculatorForm(forms.Form):
    value = forms.DecimalField(required=True)
    measure = forms.ChoiceField(required=True, choices=[("dbm", "dBm"), ("mw", "mW")])


class Calculator(CalculatorBase):
    name = "dbm2mw"
    title = "dBm to mW"
    form_class = CalculatorForm

    def calculate(self, value, measure):
        if measure == "dbm":
            r = [("dBm", value), ("mW", dbm2mw(value))]
        else:  # mW
            r = [("dBm", mw2dbm(value)), ("mW", value)]
        return r
