# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Various tags
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## Django modules
from django import template

register = template.Library()

NOCTableTemplate = """
<link rel="stylesheet" type="text/css" href="/static/css/tablesorter.css" />
<script type="text/javascript" src="/static/js/jquery.tablesorter.js"></script>
<script type="text/javascript">
$(document).ready(function() { 
    $("#%(id)s").tablesorter({
        widgets: ["zebra"],
    });
    $("#%(id)s tbody td").hover(
        function () {
            $(this).parents("tr").children("td").addClass("highlight");
        },
        function () {
            $(this).parents("tr").children("td").removeClass("highlight");
        }
    );
});
</script>
"""

rx_table = re.compile(r"<table[^>]*>", re.MULTILINE | re.DOTALL)

class NOCTableNode(template.Node):
    def __init__(self, nodelist):
        super(NOCTableNode, self).__init__()
        self.nodelist = nodelist
    
    def render(self, context):
        output = self.nodelist.render(context)
        # Get ID and class
        match = rx_table.search(output)
        if match:
            # Parse table attributes
            t = match.group(0)
            attrs = {}
            for a in [a.strip() for a in t[6:-1].split() if a.strip()]:
                if "=" in a:
                    k, v = [x.strip() for x in a.split("=", 1)]
                    if ((v[0] == "'" and v[-1] == "'") or
                        (v[0] == '"' and v[-1] == '"')):
                        v = v[1:-1]
                else:
                     k, v = a, None
                attrs[k.lower()] = v
            # Add attribute
            if "id" not in attrs:
                attrs["id"] = "tablesorter-table"
            # Add class, if necessary
            if "class" not in attrs:
                attrs["class"] = "tablesorter"
            else:
                classes = [c.strip() for c in attrs["class"].split()]
                if "tablesorter" not in classes:
                    classes += ["tablesorter"]
                    attrs["class"] = " ".join(classes)
            # Reconstruct table
            a = []
            for k, v in attrs.items():
                if v is None:
                    a += [k]
                else:
                    a += ["%s='%s'" % (k, v)]
            
            tt = "<table %s>" % " ".join(a)
            return NOCTableTemplate % attrs + output.replace(t, tt)
        else:
            # Return untouched
            return output

def do_noctable(parser, token):
    nodelist = parser.parse(("endnoctable",))
    parser.delete_first_token()
    return NOCTableNode(nodelist)

register.tag("noctable", do_noctable)
