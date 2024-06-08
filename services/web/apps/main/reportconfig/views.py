# ----------------------------------------------------------------------
# main.report application
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Optional, Set
from collections import defaultdict

# Third-party modules
from django.http import HttpResponse, HttpResponseBadRequest

# NOC modules
from noc.services.web.base.extdocapplication import ExtDocApplication, view
from noc.main.models.report import Report
from noc.core.reporter.base import ReportEngine
from noc.core.reporter.types import RunParams, OutputType
from noc.core.translation import ugettext as _
from noc.models import get_model
from noc.config import config


class ReportConfigApplication(ExtDocApplication):
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
                queries = []
                for q in b.get("queries") or []:
                    if q["datasource"]:
                        q["datasource__label"] = q["datasource"]
                    queries += [q]
                b["queries"] = queries
                if b["name"] == "Root":
                    r["root_orientation"] = b.get("orientation")
                    r["root_queries"] = b.get("queries") or []
                    continue
                elif b["parent"] == "Root":
                    b.pop("parent")
                bands += [b]
            r["bands"] = bands
            r["localization"] = []
            for field, items in o.localization.items():
                for lang, value in items.items():
                    r["localization"] += [
                        {"field": field, "language": lang, "language__label": lang, "value": value}
                    ]
            if r.get("report_source"):
                r["report_source__label"] = r["report_source"]
        for x in r.get("parameters", []):
            if x.get("model_id"):
                x["model_id__label"] = x["model_id"]
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
        localization = defaultdict(dict)
        for row in data.get("localization"):
            localization[row["field"]][row["language"]] = row["value"]
        data["localization"] = localization
        return super().clean(data)

    @staticmethod
    def get_columns_filter(
        report: "Report",
        checked: Optional[Set[str]] = None,
        pref_lang: Optional[str] = None,
    ):
        """
        Get columns filter
        :param report:
        :param checked:
        :param pref_lang:
        :return:
        """
        r = []
        checked = checked or {}
        root_fmt = report.get_band_format()
        if not root_fmt.column_format:
            return r
        columns = report.get_band_columns()
        for field in root_fmt.column_format:
            field_name = field["name"]
            if "." in field_name:
                q_name, fn = field_name.split(".")
            else:
                q_name, fn = "", field_name
            if q_name not in columns:
                continue
            elif fn not in columns[q_name] and fn not in {"all", "*"}:
                continue
            title = (
                report.get_localization(f"columns.{field_name}", lang=pref_lang)
                or field.get("title")
                or field_name
            )
            r += [(field_name, title, field_name in checked)]
        return r

    @view(url=r"^(?P<report_id>\S+)/form/$", method=["GET"], access="run", api=True)
    def api_form_report(self, request, report_id):
        report: "Report" = self.get_object_or_404(Report, id=report_id)
        pref_lang = request.user.preferred_language
        outputs = set()
        r = {
            "title": report.get_localization(field="title", lang=pref_lang),
            "description": report.description,
            "params": [],
            "preview": False,
            "dockedItems": [
                # {"text": "csv", "param": {"output_type": "csv"}},
                # {"text": "ssv", "param": {"output_type": "xlsx"}},
            ],
        }
        tpl = report.templates[0] if report.templates else None
        if tpl and tpl.output_type:
            outputs.add(tpl.output_type.lower())
        if report.report_source or (tpl and tpl.has_preview):
            r["preview"] = True
            r["dockedItems"] += [{"text": "Preview", "param": {"output_type": "html"}}]
            outputs.discard("html")
        if report.report_source or (tpl and tpl.is_alterable_output):
            outputs.update({"csv", "csv+zip", "xlsx"})
        if outputs:
            r["dockedItems"] += [
                {"text": out.upper(), "param": {"output_type": out}} for out in outputs
            ]
        for param in report.parameters:
            if param.hide:
                continue
            cfg = {
                "name": param.name,
                "fieldLabel": report.get_localization(
                    f"parameters.{param.name}",
                    lang=pref_lang,
                )
                or param.label,
                "allowBlank": not param.required,
                "uiStyle": "medium",
            }
            if param.type == "model":
                model = get_model(param.model_id)
                if hasattr(model, "get_path"):
                    cfg["xtype"] = "noc.core.combotree"
                    cfg["restUrl"] = f'/{"/".join(param.model_id.lower().split("."))}/'
                    cfg["uiStyle"] = "large"
                else:
                    cfg["xtype"] = "core.combo"
                    cfg["restUrl"] = f'/{"/".join(param.model_id.lower().split("."))}/lookup/'
                    cfg["uiStyle"] = "medium-combo"
            elif param.type == "model_multi":
                model = get_model(param.model_id)
                cfg["xtype"] = "core.tagfield"
                cfg["url"] = f'/{"/".join(param.model_id.lower().split("."))}/'
                cfg["displayField"] = "name"
                cfg["uiStyle"] = "large"
            elif param.type == "integer":
                cfg["xtype"] = "numberfield"
                cfg["uiStyle"] = "small"
                if param.default:
                    cfg["value"] = int(param.default)
            elif param.type == "date":
                cfg["xtype"] = "datefield"
                cfg["format"] = "d.m.Y"
                cfg["submitFormat"] = "d.m.Y"
            elif param.type == "choice":
                cfg["xtype"] = "radiogroup"
                cfg["items"] = [
                    {"boxLabel": x, "inputValue": x, "checked": x == param.default}
                    for x in param.choices
                ]
            elif param.type == "bool":
                cfg["xtype"] = "checkbox"
                cfg["uiStyle"] = "small"
            elif param.type == "fields_selector":
                cf = self.get_columns_filter(
                    report,
                    checked={p.strip() for p in param.default.split(",")},
                    pref_lang=pref_lang,
                )
                cfg["xtype"] = "reportcolumnselect"
                cfg["storeData"] = cf
            else:
                cfg["xtype"] = "textfield"
            r["params"] += [cfg]
        # formats
        return r

    @view(method=["GET"], url=r"^(?P<report_id>\S+)/run/$", access="run", api=True)
    def api_report_run(self, request, report_id: str):
        """

        :param request:
        :param report_id:
        :return:
        """
        q = {str(k): v[0] if len(v) == 1 else v for k, v in request.GET.lists()}
        pref_lang = request.user.preferred_language
        report: "Report" = self.get_object_or_404(Report, id=report_id)
        report_engine = ReportEngine(
            report_execution_history=config.web.enable_report_history,
        )
        rp = RunParams(
            report=report.get_config(pref_lang),
            output_type=OutputType(q.get("output_type")),
            params=q,
        )
        try:
            out_doc = report_engine.run_report(r_params=rp)
        except ValueError as e:
            return HttpResponseBadRequest(e)
        content = out_doc.get_content()
        response = HttpResponse(content, content_type=out_doc.content_type)
        response["Content-Disposition"] = f'attachment; filename="{out_doc.document_name}"'
        return response
