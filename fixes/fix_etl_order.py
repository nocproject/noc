# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Fix ETL extraction sorting order
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import os
import shutil
import glob
import gzip
import csv

PATTERNS = [
    "var/import/*/*/import.csv.gz",
    "var/import/*/*/archive/*.csv.gz",
]


def fix():
    for pattern in PATTERNS:
        for path in glob.glob(pattern):
            print("Fixing order in %s:" % path)
            tmp_path = path + "~"
            with gzip.open(path, "r") as f_in:
                reader = csv.reader(f_in)
                data = sorted(row for row in reader)
            with gzip.open(tmp_path, "w") as f_out:
                writer = csv.writer(f_out)
                writer.writerows(data)
            os.unlink(path)
            shutil.move(tmp_path, path)
            print("    ... done")
