#!./bin/python
# ----------------------------------------------------------------------
# Compile handlebars templates
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

import glob
# Python modules
import os
import stat
import subprocess


def compile_template(src):
    dst = src[:-4] + ".js"
    if os.path.exists(dst) and os.stat(src)[stat.ST_MTIME] < os.stat(dst)[stat.ST_MTIME]:
        return  # Up-to-date
    parts = src.split(os.sep)
    module = parts[2]
    app = parts[3]
    name = parts[-1][:-4]
    print("%s -> %s" % (src, dst))
    tmp = dst + ".tmp"
    subprocess.check_call([
        "handlebars",
        "-m",  # Minify
        "-n", "NOC.templates.%s_%s" % (module, app),
        "-e", "hbs",
        "-f", tmp,
        src
    ])
    with open(tmp) as f:
        data = f.read()
    os.unlink(tmp)
    data += "Ext.define(\"NOC.%s.%s.templates.%s\", {});" % (module, app, name)
    with open(dst, "w") as f:
        f.write(data)


def main():
    for f in glob.glob("ui/web/*/*/templates/*.hbs"):
        compile_template(f)


if __name__ == "__main__":
    main()
