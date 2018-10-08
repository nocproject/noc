# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Span handler
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import operator
import datetime
# NOC modules
from base import BaseCard
from noc.core.clickhouse.connect import connection


class Span(object):
    def __init__(self, ts, id, parent, server, service, client,
                 duration, sample, error_code, error_text,
                 in_label, out_label):
        self.ts = datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        self.id = int(id)
        self.parent = int(parent) if parent else None
        self.server = server
        self.service = service
        self.client = client
        self.duration = int(duration)
        self.sample = int(sample)
        self.error_code = error_code
        self.error_text = error_text.replace("\\r", "<br>").replace("\\n", "<br>").replace('\\', '')
        self.in_label = in_label.replace("\\r", "<br>").replace("\\n", "<br>").replace('\\', '')
        self.out_label = out_label.replace("\\r", "<br>").replace("\\n", "<br>").replace('\\', '')
        self.children = []
        self.level = 0
        self.left = 0
        self.width = 0


class SpanCard(BaseCard):
    name = "span"
    default_template_name = "span"

    GRAPH_WIDTH = 400

    def get_data(self):
        # Get span data
        ch = connection()
        data = [
            Span(*r)
            for r in ch.execute("""
              SELECT
                ts, id, parent, server, service, client,
                duration, sample, error_code,
                error_text, in_label, out_label
              FROM span
              WHERE ctx = %s""", [int(self.id)])
        ]
        # Build hierarchy
        smap = dict((s.id, s) for s in data)
        root = None
        for s in data:
            if s.parent:
                smap[s.parent].children += [s]
            else:
                root = s
        # Set width
        for s in data:
            if s.parent:
                d = s.ts - root.ts
                dt = d.seconds * 1000000 + d.microseconds
                s.left = self.GRAPH_WIDTH * dt // root.duration
                s.width = int(float(self.GRAPH_WIDTH) / (float(root.duration) / float(s.duration)))
            else:
                s.left = 0
                s.width = self.GRAPH_WIDTH
        # Flatten
        spans = self.flatten_spans(root)
        #
        return {
            "context": int(self.id),
            "root": root,
            "spans": spans
        }

    def flatten_spans(self, span, level=0):
        span.level = level
        r = [span]
        for c in sorted(span.children, key=operator.attrgetter("ts")):
            r += self.flatten_spans(c, level + 1)
        return r
