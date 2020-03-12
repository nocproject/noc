#!/usr/bin/env python
# USAGE: build <spec>

import tarfile
import json
import sys
import os
import glob
import shutil

def build(spath):
    with open(spath) as f:
        spec = json.load(f)
    pkg = spec["name"]
    version = os.environ.get("CI_BUILD_REF")
    src_prefix = spec["src_prefix"]
    dst_prefix = spec["dst_prefix"]
    if dst_prefix.startswith("/"):
        dst_prefix = dst_prefix[1:]
    dist_path = os.path.join("dist", "%s@%s.tar.bz2" % (pkg, version))
    tmp_path = dist_path + ".tmp"
    tf = tarfile.open(tmp_path, "w:bz2")
    src_root = "src"
    p = os.path.join(src_root, src_prefix)
    if not p.endswith("/"):
        p += "/"
    pl = len(p)
    for f in spec["files"]:
        gf = os.path.join(p, f)
        for ff in glob.glob(gf):
            rn = ff[pl:]
            tn = os.path.join(dst_prefix, rn)
            print ff, "->", tn
            tf.add(ff, tn, recursive=True)
    tf.close()
    print "Writing dist_path"
    shutil.move(tmp_path, dist_path)


if __name__ == "__main__":
    build(sys.argv[1])


