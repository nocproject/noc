# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## .. supported:: Profile
## extension
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from __future__ import with_statement
from sphinx.util.compat import Directive
from docutils import nodes
import csv

class supported(nodes.Element): pass

class Supported(Directive):
    has_content=True
    required_arguments=1
    def run(self):
        node=supported()
        node.document=self.state.document
        node.line=self.lineno
        node["profile"]=self.arguments[0]
        return [node]

def html_visit_supported(self,node):
    body=[]
    reader=csv.reader(open("../../../../local/supported.csv"))
    profile=node["profile"]
    se={}
    for r in [l for l in reader if l[0]==profile]:
        profile,model,version=r
        if model not in se:
            se[model]=set()
        se[model].add(version)
    body+=["<table border=\"1\" class=\"docutils\">"]
    for m in sorted(se.keys()):
        body+=["<tr><td>%s</td><td>%s</td></tr>"%(m,", ".join(sorted(se[m])))]
    body+=["</table>"]
    self.body.append("\n".join(body))
    raise nodes.SkipNode

def setup(app):
    app.add_node(supported,
        html=(html_visit_supported,None)
        )
    app.add_directive("supported",Supported)
