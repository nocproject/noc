# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CSV Parser
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import csv
import noc.kb.parsers

##
## Creole Parser
##
class Parser(noc.kb.parsers.Parser):
    name="CSV"
    @classmethod
    def to_html(cls,kb_entry):
        reader=csv.reader([l.encode("utf-8") for l in kb_entry.body.splitlines()])
        r=["<TABLE BORDER='1'>"]
        for row in reader:
            r+=[u"<TR>"]+[u"<TD>%s</TD>"%unicode(c,"utf-8") for c in row]+[u"</TR>"]
        r+=[u"</TABLE>"]
        return "".join(r)
