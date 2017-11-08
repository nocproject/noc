# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Fix ETL extraction sorting order
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import csv
import glob
import gzip
# Python modules
import os
import shutil

from noc.config import config

PATTERNS = [
    "%s/*/*/import.csv.gz" % config.path.etl_import,
    "%s/*/*/archive/*.csv.gz" % config.path.etl_import,
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
