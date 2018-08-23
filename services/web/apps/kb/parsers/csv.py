# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# CSV Parser
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import csv
# NOC modules
from .base import BaseParser


class CSVParser(BaseParser):
    name = "CSV"

    @classmethod
    def to_html(cls, kb_entry):
        reader = csv.reader([l.encode("utf-8") for l in kb_entry.body.splitlines()])
        r = [u"<TABLE BORDER='1' ID='csvtable' class='tablesorter'>", "<thead>"]
        r += [u"<TR>"] + [u"<TH>%s</TH>" % unicode(c, "utf-8") for c in next(reader)] + [u"</TR>"]
        r += [u"</thead>", u"<tbody>"]
        for row in reader:
            r += [u"<TR>"] + [u"<TD>%s</TD>" % unicode(c, "utf-8") for c in row] + [u"</TR>"]
        r += [u"</tbody></TABLE>"]
        r += [u"<script type='text/javascript'>",
              u"$(document).ready(function() {$('#csvtable').tablesorter();});",
              u"</script>"]
        return "".join(r)
