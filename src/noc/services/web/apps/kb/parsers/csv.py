# ---------------------------------------------------------------------
# CSV Parser
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import csv

# NOC modules
from noc.core.comp import smart_text
from .base import BaseParser


class CSVParser(BaseParser):
    name = "CSV"

    @classmethod
    def to_html(cls, kb_entry):
        reader = csv.reader(list(kb_entry.body.splitlines()))
        r = ["<TABLE BORDER='1' ID='csvtable' class='tablesorter'>", "<thead>"]
        r += ["<TR>"] + [f"<TH>{smart_text(c)}</TH>" for c in next(reader)] + ["</TR>"]
        r += ["</thead>", "<tbody>"]
        for row in reader:
            r += ["<TR>"] + [f"<TD>{smart_text(c)}</TD>" for c in row] + ["</TR>"]
        r.append("</tbody></TABLE>")
        r += [
            "<script type='text/javascript'>",
            "$(document).ready(function() {$('#csvtable').tablesorter();});",
            "</script>",
        ]
        return "".join(r)
