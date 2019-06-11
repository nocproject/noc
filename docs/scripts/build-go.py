# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Build go.html
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import sys
import os
# Third-party modules
from sphinx.util.inventory import InventoryFile

JS = """
function redirect(rmap) {
var href = window.location.href;
var label = href.split('#')[1];
var base = href.substr(0, href.indexOf("go.html"))
window.location = base + rmap[label];
}
"""


def process(path):
    r = [
        "<html>", "<head>", "<title>NOC go</title>", "</head>", "<body>",
        "<script>", JS, "redirect({"
    ]
    with open(path) as f:
        data = InventoryFile.load(f, "", os.path.join) or {}
    rr = []
    for entry, einfo in sorted(data["std:label"].items()):
        rr += ["'%s': '%s'" % (entry, einfo[2])]
    r += [",".join(rr), "});", "</script>", "</body>", "</html>"]
    base = os.path.dirname(path)
    go_path = os.path.join(base, "go.html")
    with open(go_path, "w") as f:
        f.write("".join(r))


if __name__ == "__main__":
    process(sys.argv[1])

