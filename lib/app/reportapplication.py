# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# ReportApplication implementation
# ---------------------------------------------------------------------
# Copyright (C) 2007-2012 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from application import Application, view
from noc.core.translation import ugettext as _


class ReportApplication(Application):
    # django.forms.Form class for report queries
    form = None
=======
##----------------------------------------------------------------------
## ReportApplication implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from application import *


class ReportApplication(Application):
    form = None # django.forms.Form class for report queries
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    content_types = {
        "text": "text/plain; charset=utf-8",
        "html": "text/html; charset=utf-8",
        "csv": "text/csv; charser=utf-8",
        }
<<<<<<< HEAD
    # List of CSS links
    styles = []
    # Inline CSS
    inline_styles = ""
=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

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

<<<<<<< HEAD
    def report_html(self, request, result, query):
        """
        Returns render report as HTML
        :param request: HTTP Request
=======
    def report_html(self, result, query):
        """
        Returns render report as HTML
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        :param result:
        :param query:
        :return:
        """
        pass

    def get_menu(self):
<<<<<<< HEAD
        return [_("Reports"), unicode(self.title)]
=======
        return "Reports | " + unicode(self.title)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

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
                return self.render(request, "report_form.html",
<<<<<<< HEAD
                                   form=form, app=self, is_report=True,
                                   styles=self.styles,
                                   inline_styles=self.inline_styles)
                # Build result
        rdata = getattr(self, "report_%s" % format)(request=request, **query)
=======
                                   form=form, app=self, is_report=True)
                # Build result
        rdata = getattr(self, "report_%s" % format)(**query)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Render result
        if format == "html":
            return self.render(request, "report.html",
                               data=rdata, app=self, is_report=True)
        else:
            return self.render_response(rdata,
                                        content_type=self.content_types[format])
