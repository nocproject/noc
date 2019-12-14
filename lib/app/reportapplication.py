# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ReportApplication implementation
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import

# NOC modules
from noc.core.translation import ugettext as _
from noc.core.comp import smart_text
from .application import Application, view


class ReportApplication(Application):
    # django.forms.Form class for report queries
    form = None
    content_types = {
        "text": "text/plain; charset=utf-8",
        "html": "text/html; charset=utf-8",
        "csv": "text/csv; charser=utf-8",
    }
    # List of CSS links
    styles = []
    # Inline CSS
    inline_styles = ""

    def __init__(self, site):
        super(ReportApplication, self).__init__(site)
        site.reports += [self]

    def get_form(self):
        return self.form

    def supported_formats(self):
        """
        Return a list of supported formats
        :return:
        """
        return [f[7:] for f in dir(self) if f.startswith("report_")]

    def get_data(self, **kwargs):
        """
        Return report results to render
        Overriden in subclasses
        :param kwargs:
        :return:
        """
        pass

    def report_html(self, request, result, query):
        """
        Returns render report as HTML
        :param request: HTTP Request
        :param result:
        :param query:
        :return:
        """
        pass

    def get_menu(self):
        return [_("Reports"), smart_text(self.title)]

    @view(url=r"^$", url_name="view", access="view", menu=get_menu)
    def view_report(self, request, format="html"):
        """
        Render report
        :param request:
        :param format:
        :return:
        """
        query = {}
        # Check format is valid for application
        if format not in self.supported_formats():
            return self.response_not_found("Unsupported format '%s'" % format)
            # Display and check form if necessary
        form_class = self.get_form()
        if form_class:
            if request.POST:
                # Process POST request and validate data
                form = form_class(request.POST)
                if form.is_valid():
                    query = form.cleaned_data
            else:
                form = form_class()
                # No POST or error - render form
            if not query:
                return self.render(
                    request,
                    "report_form.html",
                    form=form,
                    app=self,
                    is_report=True,
                    styles=self.styles,
                    inline_styles=self.inline_styles,
                )
                # Build result
        rdata = getattr(self, "report_%s" % format)(request=request, **query)
        # Render result
        if format == "html":
            return self.render(request, "report.html", data=rdata, app=self, is_report=True)
        else:
            return self.render_response(rdata, content_type=self.content_types[format])
