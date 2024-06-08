# ---------------------------------------------------------------------
# ReportApplication implementation
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import logging

# NOC modules
from noc.core.translation import ugettext as _
from noc.core.middleware.tls import get_user
from .application import Application, view
from .access import Permission


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
        super().__init__(site)
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

    def report_html(self, request, result, query):
        """
        Returns render report as HTML
        :param request: HTTP Request
        :param result:
        :param query:
        :return:
        """

    def get_menu(self):
        return [_("Reports"), self.title]

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
        return self.render_response(rdata, content_type=self.content_types[format])


class ReportByConfigApplication(Application):
    """
    Report Config application
    """

    CATEGORY_MAP = {"main", "fm", "sa", "inv", "sla"}

    report_id: str = None
    report_config = None

    def __init__(self, site):
        self.site = site
        self.service = None  # Set by web
        self.module = self.get_module()
        self.app = self.report_id
        self.module_title = self.report.name
        self.app_id = f"{self.module}.{self.app}"
        self.menu_url = None  # Set by site.autodiscover()
        self.logger = logging.getLogger(self.app_id)
        self.j2_env = None

    @property
    def title(self) -> str:
        user = get_user()
        return (
            self.report.get_localization(
                field="title",
                lang=user.preferred_language if user else None,
            )
            or self.report.title
            or self.report.name
        )

    @property
    def menu(self):
        return [_("Reports"), self.title]

    @classmethod
    def get_report_config(cls):
        """
        Return Report Config by Report Id
        :return:
        """
        from noc.main.models.report import Report

        if not cls.report_config:
            cls.report_config = Report.get_by_id(cls.report_id)
        return cls.report_config

    @property
    def report(self):
        return self.get_report_config()

    @classmethod
    def get_module(cls) -> str:
        report_config = cls.get_report_config()
        if report_config.category in cls.CATEGORY_MAP:
            return report_config.category
        return "main"

    @classmethod
    def get_app_id(cls):
        """
        Returns application id
        """
        return f"main.{cls.report_id}"

    @property
    def js_app_class(self):
        return "NOC.main.desktop.Report"

    @property
    def launch_access(self):
        return ReportPermit()

    def get_launch_info(self, request):
        """
        Return desktop launch information
        """

        r = super().get_launch_info(request)
        r["params"]["report_id"] = self.report_id
        return r

    def get_permissions(self):
        return set()


class ReportPermit(Permission):
    """
    Always permit
    """

    def check(self, app: "ReportByConfigApplication", user, obj=None) -> bool:
        from noc.main.models.report import Report

        reports = Report.get_effective_permissions(user)
        return app.report_id in reports
