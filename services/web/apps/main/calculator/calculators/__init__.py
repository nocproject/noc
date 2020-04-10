# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Calculators framework
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.lib.registry import Registry


class CalculatorRegistry(Registry):
    name = "CalculatorRegistry"
    subdir = "calculator/calculators"
    classname = "Calculator"
    apps = ["noc.main"]


calculator_registry = CalculatorRegistry()


class CalculatorBase(type):
    def __new__(cls, name, bases, attrs):
        m = type.__new__(cls, name, bases, attrs)
        calculator_registry.register(m.name, m)
        return m


class Calculator(object, metaclass=CalculatorBase):
    name = None
    title = None
    description = None
    form_class = None
    template = "calculator.html"

    def __init__(self, app):
        self.app = app

    def render(self, request):
        result = None
        if request.POST:
            form = self.form_class(request.POST)
            if form.is_valid():
                result = self.calculate(**form.cleaned_data)
        else:
            form = self.form_class()
        return self.app.render(
            request,
            self.template,
            form=form,
            title=self.title,
            result=result,
            description=self.description,
        )

    def calculate(**kwargs):
        """
        Returns a list of pairs or None
        :param kwargs:
        :return:
        """
        return None
