# ----------------------------------------------------------------------
# Base BI extractor
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os
import datetime
import itertools
import gzip

# Third-party modules
import orjson

# NOC modules
from noc.config import config
from noc.core.fileutils import make_persistent


class Stream(object):
    CHUNK_SIZE = config.bi.chunk_size

    def __init__(self, model, prefix, date=None):
        self.prefix = prefix
        self.model = model
        self.date = date or datetime.date.today()
        self.chunk_count = itertools.count()
        self.out = None
        self.out_path = None
        now = datetime.datetime.now()
        self.fs = "%s-%s" % (self.model._meta.db_table, now.strftime("%Y-%m-%d-%H-%M-%S-%f"))
        self.chunk_size = 0
        self.ts_field = self.model._meta.ordered_fields[1].name

    def __del__(self):
        if self.out:
            os.unlink(self.out_path)

    def push(self, date=None, **kwargs):
        if not date:
            if self.ts_field:
                ts = kwargs[self.ts_field]
                date = datetime.date(year=ts.year, month=ts.month, day=ts.day)
        if not self.out:
            self.out_path = os.path.join(
                self.prefix, "%s-%06d.jsonl.gz.tmp" % (self.fs, next(self.chunk_count))
            )
            self.out = gzip.open(self.out_path, "wb")
            self.chunk_size = 0
        self.out.write(orjson.dumps(self.model.to_json(date=date, **kwargs)))
        self.out.write(b"\n")
        self.chunk_size += 1
        if self.chunk_size == self.CHUNK_SIZE:
            self.out.close()
            make_persistent(self.out_path)
            self.out = None

    def finish(self):
        if self.out:
            self.out.close()
            make_persistent(self.out_path)
            self.out = None
