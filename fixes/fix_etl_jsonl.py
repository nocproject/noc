# ----------------------------------------------------------------------
# Fix ETL format to JSONL
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import csv

# NOC modules
from noc.core.compressor.loader import loader as comp_loader
from noc.core.etl.models.loader import loader as model_loader
from noc.config import config


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


def ensure_format(path):
    comp = comp_loader[config.etl.compression]
    if comp.ext:
        if not path.endswith(comp.ext):
            return
        s_path = path[: -len(comp.ext)]
    else:
        s_path = path
    if not s_path.endswith(".csv"):
        return  # Already completed
    parts = os.path.dirname(path).split(os.sep)
    if parts[-1] == "archive":
        name = parts[-2]
    else:
        name = parts[-1]
    model = model_loader[name]
    new_path = comp.get_path("%s.jsonl" % s_path[:-4])
    with comp(path).open() as f:
        reader = csv.reader(f)
        next(reader)  # Skip headers
        with comp(new_path, "w").open() as ff:
            for n, row in enumerate(reader):
                data = model.from_iter(row)
                if n:
                    ff.write("\n%s" % data.json(exclude_defaults=True, exclude_unset=True))
                else:
                    ff.write(data.json(exclude_defaults=True, exclude_unset=True))
    os.unlink(path)
