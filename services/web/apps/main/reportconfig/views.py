# ----------------------------------------------------------------------
# main.report application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Third-party modules
from django.http import HttpResponse

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.sa.interfaces.base import StringParameter, DictParameter
from noc.main.models.report import Report
from noc.core.reporter.base import ReportEngine
from noc.core.reporter.types import RunParams, OutputType
from noc.core.translation import ugettext as _
from noc.models import get_model


class ReportApplication(ExtDocApplication):
    """
    Report application
    """

    title = "Report Configs"
    menu = _("Report Config")
    model = Report

    def instance_to_dict(self, o, fields=None, nocustom=False):
        r = super().instance_to_dict(o, fields, nocustom)
        if isinstance(o, Report):
            bands = []
            for b in r["bands"]:
                if b["name"] == "Root":
                    r["root_orientation"] = b.get("orientation")
                    r["root_queries"] = b.get("queries") or []
                    continue
                elif b["parent"] == "Root":
                    b.pop("parent")
                bands += [b]
            r["bands"] = bands
        return r

    def clean(self, data):
        bands = [
            {
                "name": "Root",
                "orientation": data.pop("root_orientation", None) or "H",
                "queries": data.pop("root_queries", None) or [],
            }
        ]
        for b in data.get("bands") or []:
            if not b.get("parent"):
                b["parent"] = "Root"
            bands += [b]
        data["bands"] = bands
        return super().clean(data)

    @view(url=r"^(?P<report_id>\S+)/form/$", method=["GET"], access="launch", api=True)
    def api_form_report(self, request, report_id):
        report: "Report" = self.get_object_or_404(Report, id=report_id)
        r = {
            "title": report.name,
            "description": report.description,
            "params": [],
            "preview": False,
            "buttons": [
                {"title": "xslx", "param": {"output_type": "xslx"}},
                {"title": "csv", "param": {"output_type": "csv"}},
            ],
        }
        if report.format == "S":
            r["preview"] = True
            r["buttons"] += [{"title": "Preview", "param": {"output_type": "html"}}]
        for param in report.parameters:
            cfg = {"name": param.name, "fieldLabel": param.label, "allowBlank": not param.required}
            if param.type == "model":
                model = get_model(param.model_id)
                cfg["xtype"] = "core.combo"
                cfg["restUrl"] = f'/{"/".join(param.model_id.lower().split("."))}/lookup/'
            elif param.type == "integer":
                cfg["xtype"] = "numberfield"
            elif param.type == "date":
                cfg["xtype"] = "datefield"
                cfg["format"] = "d.m.Y"
                cfg["submitFormat"] = "d.m.Y"
            elif param.type == "choice":
                cfg["xtype"] = "radiogroup"
                cfg["items"] = [
                    {"boxLabel": x, "inputValue": x, "checked": x == param.default}
                    for x in param.description.split(";")
                ]
            else:
                cfg["xtype"] = "textfield"
            r["params"] += [cfg]
        if report.format == "D":
            ds = report.get_datasource()
            r["params"] += [
                {
                    "xtype": "report.control",
                    "storeData": [
                        {"name": ff.name, "active": True, "label": ff.name} for ff in ds.fields
                    ],
                }
            ]
        # formats
        return r

    @view(
        method=["GET"],
        url="^(?P<report_id>\S+)/run/$",
        access="launch",
        api=True,
        # validate={
        #     "parameters": DictParameter(
        #         attrs={"name": StringParameter(), "value": StringParameter()}, required=False
        #     ),
        #     "output_type": StringParameter(default="html"),
        # },
    )
    def api_report_run(self, request, report_id: str):
        """

        :param request:
        :param report_id:
        :param query:
        :return:
        """
        q = {str(k): v[0] if len(v) == 1 else v for k, v in request.GET.lists()}
        report: "Report" = self.get_object_or_404(Report, id=report_id)
        report_engine = ReportEngine()
        rp = RunParams(report=report.config, output_type=OutputType(q.get("output_type")))
        out_doc = report_engine.run_report(r_params=rp)
        response = HttpResponse(out_doc.content, content_type=out_doc.content_type)
        response["Content-Disposition"] = f'attachment; filename="{out_doc.document_name}"'
        return response
