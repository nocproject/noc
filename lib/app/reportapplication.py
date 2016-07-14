# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ReportApplication implementation
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# NOC modules
from application import Application, view
from noc.core.translation import ugettext as _


class ReportApplication(Application):
    form = None # django.forms.Form class for report queries
    content_types = {
        "text": "text/plain; charset=utf-8",
        "html": "text/html; charset=utf-8",
        "csv": "text/csv; charser=utf-8",
        }

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

    def report_html(self, result, query):
        """
        Returns render report as HTML
        :param result:
        :param query:
        :return:
        """
        pass

    def get_menu(self):
        return [_("Reports"), unicode(self.title)]

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
                                   form=form, app=self, is_report=True)
                # Build result
        rdata = getattr(self, "report_%s" % format)(**query)
        # Render result
        if format == "html":
            return self.render(request, "report.html",
                               data=rdata, app=self, is_report=True)
        else:
            return self.render_response(rdata,
                                        content_type=self.content_types[format])
