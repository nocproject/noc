# ----------------------------------------------------------------------
# Fix ETL file/compression format
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
import os

# NOC modules
from noc.core.compressor.loader import loader
from noc.config import config

ext_map = {
    cc.ext: cc for cc in (loader[c] for c in loader.iter_classes()) if cc and cc.ext is not None
}


def fix():
    root = config.path.etl_import
    if not os.path.exists(root):
        return  # Nothing to convert
    for rs in os.listdir(root):
        rs_root = os.path.join(root, rs)
        for d in os.listdir(rs_root):
            sys_root = os.path.join(root, rs, d)
            if not os.path.exists(sys_root):
                continue
            imports = [f for f in os.listdir(sys_root) if f.startswith("import.csv")]
            if "import.csv" in imports:
                ensure_format(os.path.join(sys_root, "import.csv"))
            elif len(imports) == 1:
                ensure_format(os.path.join(sys_root, imports[0]))
            arch_root = os.path.join(sys_root, "archive")
            if not os.path.exists(arch_root):
                continue
            archives = {f for f in os.listdir(arch_root) if f.startswith("import-")}
            for f in archives:
                ensure_format(os.path.join(arch_root, f))


def ensure_format(path: str) -> None:
    dst_comp = loader[config.etl.compression]
    if path.endswith(dst_comp.ext) and (path.endswith(".csv") and not dst_comp.ext):
        print("[%s] Already compressed" % path)
        return  # Already compressed
    src_ext = ""
    for ext in ext_map:
        if path.endswith(ext) or (path.endswith(".csv") and not ext):
            src_ext = ext
            break
    if src_ext == dst_comp.ext:
        print("[%s] Already compressed. Skipping" % path)
        return
    src_comp = ext_map[src_ext]
    dst_path = path[: -len(src_ext) if src_ext else None] + dst_comp.ext
    print("Repacking %s -> %s" % (path, dst_path))
    with src_comp(path, "r") as src, dst_comp(dst_path, "w") as dst:
        dst.write(src.read())
    os.unlink(path)
