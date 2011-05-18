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
from django.utils.safestring import SafeString
## NOC modules
from noc.sa.models import ManagedObject

register = template.Library()

NOCTableTemplate = """
<link rel="stylesheet" type="text/css" href="/static/css/tablesorter.css" />
<script type="text/javascript" src="/static/js/jquery.tablesorter.js"></script>
<script type="text/javascript">
$(document).ready(function() {
    $.tablesorter.addParser({
        id: "switchPort",
        is: function (s) {
            return /^\d{1,2}:\d{1,2}$/.test(s);
        },
        format: function (s) {
            var a = s.split(":"),
                r = "",
                l = a.length;
            for (var i = 0; i < l; i++) {
                var item = a[i];
                if (item.length == 2) {
                    r += "0" + item;
                } else {
                    r += item;
                }
            }
            return $.tablesorter.formatFloat(r);
        },
        type: "numeric"
    });
    $("#%(id)s").tablesorter({
        widgets: ["zebra"],
    });
    $("#tablesorter-search").focus();
    $("#%(id)s tbody td").hover(
        function () {
            $(this).parents("tr").children("td").addClass("highlight");
        },
        function () {
            $(this).parents("tr").children("td").removeClass("highlight");
        }
    );
});

function startswith(s, ss) {
    s.substr(0, ss.length) == ss;
}

var ts_last_search = "";
function ts_on_search(s) {
    var search = s.value;
    if(search == ts_last_search)
        return;
    var all_seen = search == "";
    var $tbody = $(s).parents(".tablesorter-container").find("tbody");
    var scope = "tr";
    if(startswith(search, ts_last_search)) {
        scope = "tr:visible";
    } else if (startswith(ts_last_search, search)) {
        scope = "tr:hidden";
    }
    $tbody.find(scope).each(function (i, r) {
        var $r = $(r);
        var seen = all_seen;
        if(!seen) {
            $r.children("td").each(function (j, d) {
                seen = $(d).text().indexOf(search) > 0;
                return !seen;
            });
        }
        if(seen) {
            $r.show();
        } else {
            $r.hide();
        }
    });
    ts_last_search = search;
}
</script>
<div class="tablesorter-container">
<div class="tablesorter-search-row">
    <label for="tablesorter-search"><img src="/media/img/admin/icon_searchbox.png" alt="Search" /></label>
    <input type="text" id="tablesorter-search" onkeyup="ts_on_search(this);"/>
</div>
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
            return NOCTableTemplate % attrs + output.replace(t, tt) + "</div>"
        else:
            # Return untouched
            return output


def do_noctable(parser, token):
    nodelist = parser.parse(("endnoctable",))
    parser.delete_first_token()
    return NOCTableNode(nodelist)

register.tag("noctable", do_noctable)


def object_name(value):
    o = ManagedObject.objects.get(id=int(value))
    return o.name

register.filter("object_name", object_name)


def bool_icon(value):
    if value is None:
        return "?"
    elif value:
        return SafeString("<img src='/media/img/admin/icon-yes.gif' alt='Yes' />")
    else:
        return SafeString("<img src='/media/img/admin/icon-no.gif' alt='No' />")

register.filter("bool_icon", bool_icon)