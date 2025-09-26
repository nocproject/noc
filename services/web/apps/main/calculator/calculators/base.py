# ---------------------------------------------------------------------
# Calculators framework
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


class BaseCalculator(object):
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
        return
