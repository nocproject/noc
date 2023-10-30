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
        reader = csv.reader([ll for ll in kb_entry.body.splitlines()])
        r = ["<TABLE BORDER='1' ID='csvtable' class='tablesorter'>", "<thead>"]
        r += ["<TR>"] + ["<TH>%s</TH>" % smart_text(c) for c in next(reader)] + ["</TR>"]
        r += ["</thead>", "<tbody>"]
        for row in reader:
            r += ["<TR>"] + ["<TD>%s</TD>" % smart_text(c) for c in row] + ["</TR>"]
        r += ["</tbody></TABLE>"]
        r += [
            "<script type='text/javascript'>",
            "$(document).ready(function() {$('#csvtable').tablesorter();});",
            "</script>",
        ]
        return "".join(r)
