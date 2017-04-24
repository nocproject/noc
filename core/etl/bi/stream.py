# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Base BI extractor
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import datetime
import itertools
import gzip
import shutil


class Stream(object):
    CHUNK_SIZE = 1000000

    def __init__(self, model, prefix, date=None):
        self.prefix = prefix
        self.model = model
        self.date = date or datetime.date.today()
        self.chunk_count = itertools.count()
        self.out = None
        self.out_path = None
        now = datetime.datetime.now()
        self.fs = "%s-%s" % (
            self.model.get_short_fingerprint(),
            now.strftime("%Y-%m-%d-%H-%M-%S-%f")
        )
        self.meta = self.model.get_fingerprint()
        self.chunk_size = 0
        self.ts_field = self.model._fields_order[1]

    def __del__(self):
        if self.out:
            os.unlink(self.out_path)

    def push(self, date=None, **kwargs):
        if not date:
            if self.ts_field:
                ts = kwargs[self.ts_field]
                date = datetime.date(year=ts.year, month=ts.month,
                                     day=ts.day)
        if not self.out:
            self.out_path = os.path.join(
                self.prefix,
                "%s-%06d.tsv.gz.tmp" % (self.fs, self.chunk_count.next())
            )
            meta_path = self.out_path[:-11] + ".meta"
            with open(meta_path, "w") as f:
                f.write(self.meta)
            self.out = gzip.open(self.out_path, "wb")
            self.chunk_size = 0
        self.out.write(
            self.model.to_tsv(date=date, **kwargs)
        )
        self.chunk_size += 1
        if self.chunk_size == self.CHUNK_SIZE:
            self.out.close()
            shutil.move(self.out_path, self.out_path[:-4])
            self.out = None

    def finish(self):
        if self.out:
            self.out.close()
            shutil.move(self.out_path, self.out_path[:-4])
            self.out = None
