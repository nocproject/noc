# ---------------------------------------------------------------------
# SimpleReport implementation
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from jinja2 import Template


class SimpleReport(object):
    title = "SimpleReport"
    columns = []
    templates = {
        "REPORT_TITLE": "<h2>{{title}}</h2>\n<table>\n",
        "MASTER_DATA": "<tr><td>Some data...</td></tr>",
        "REPORT_SUMMARY": "</table>",
    }

    def prepare_templates(self):
        self.templates = {}
        self.templates["REPORT_TITLE"] = "<h2>{{title}}</h2>\n<table>\n"
        self.templates["MASTER_DATA"] = "<tr>"
        for column in self.columns:
            self.templates["REPORT_TITLE"] += f"<th>{column}</th>"
            self.templates["MASTER_DATA"] += f"<td>{{{{{column}}}}}</td>"
        self.templates["REPORT_TITLE"] += "</tr>"
        self.templates["MASTER_DATA"] += "</tr>"
        self.templates["REPORT_SUMMARY"] = "</table>"

    def get_records(self):
        """
        Rerurn list containing records for output in MASTER_DATA band.
        Must be overriden
        """
        raise NotImplementedError

    def generate_html(self):
        """
        Render HTML
        """
        self.prepare_templates()
        template_1 = self.templates["REPORT_TITLE"]
        template_2 = self.templates["MASTER_DATA"]
        template_3 = self.templates["REPORT_SUMMARY"]

        html = Template(template_1).render(title=self.title) + "\n"
        records = self.get_records()
        for record in records:
            print("record", record, type(record))
            if isinstance(record, str):
                html += f"<tr><td>{record}</td></tr>\n"
            if isinstance(record, (list, tuple)):
                params = {column: str(record[i]) for i, column in enumerate(self.columns)}
                print("params", params, type(params))
                html += Template(template_2).render(**params) + "\n"
        html += Template(template_3).render() + "\n"
        return html
