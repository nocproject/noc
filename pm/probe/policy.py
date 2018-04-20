# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Base feed policy
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import random


class FeedPolicy(object):
    def __init__(self):
        self.write_concern = 0
        self.collectors = []
        self.gen = None
        self.rri = random.randint(0, 0xFFFF)

    def configure(self, collectors):
        self.write_concern = collectors["write_concern"]
        self.collectors = [
            (c["proto"], c["address"], c["port"])
            for c in collectors["collectors"]
        ]
        self.gen = getattr(self, "iter_%s" % collectors["policy"])

    def start(self):
        return self.gen()

    def iter_all(self):
        """
        ALL policy
        """
        for c in self.collectors:
            yield c

    def iter_pri(self):
        for c, _ in zip(self.collectors, range(self.write_concern)):
            yield c

    def iter_rr(self):
        cl = len(self.collectors)
        for i in range(self.write_concern):
            yield self.collectors[self.rri % cl]
            self.rri = (self.rri + 1) % cl

    def iter_rnd(self):
        for c in random.sample(self.collectors, self.write_concern):
            yield c
