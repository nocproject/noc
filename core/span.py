# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# External call spans
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import threading
import time
import random
import os
import struct
# NOC modules
from noc.core.error import NO_ERROR, ERR_UNKNOWN
from noc.core.perf import metrics

span_lock = threading.Lock()

# Collected spans, protected by lock
SPAN_FIELDS = "date.ts.ctx.id.parent.server.service.client.duration" \
              ".error_code.error_text.sample.in_label.out_label"
tls = threading.local()
spans = []

DEFAULT_CLIENT = "NOC"
DEFAULT_SERVER = "NOC"
DEFAULT_SERVICE = "unknown"
DEFAULT_SAMPLE_RATE = 1
DEFAULT_ERROR_TEXT = ""
DEFAULT_LABEL = ""
DEFAULT_ID = 0
US = 1000000.0


class Span(object):
    def __init__(self, client=DEFAULT_CLIENT, server=DEFAULT_SERVER,
                 service=DEFAULT_SERVICE, sample=DEFAULT_SAMPLE_RATE,
                 in_label=DEFAULT_LABEL, parent=DEFAULT_ID):
        self.client = client
        self.server = server
        self.service = service
        self.sample = sample
        if not sample:
            self.is_sampled = False
        if sample == DEFAULT_SAMPLE_RATE:
            self.is_sampled = True
        else:
            self.is_sampled = random.randint(0, sample - 1) == 0
        self.start = None
        self.duration = None
        self.error_code = NO_ERROR
        self.error_text = DEFAULT_ERROR_TEXT
        self.in_label = in_label
        self.out_label = DEFAULT_LABEL
        self.parent = parent
        self.span_id = DEFAULT_ID
        self.span_context = DEFAULT_ID
        self.span_parent = DEFAULT_ID

    def __enter__(self):
        if not self.is_sampled:
            return
        # Generate span ID
        self.span_id = struct.unpack("!Q", os.urandom(8))[0]
        # Get span context
        try:
            self.span_context = tls.span_context
            # Get parent
            try:
                self.span_parent = tls.span_parent
                if self.parent == DEFAULT_ID:
                    self.parent = self.span_parent
            except AttributeError:
                pass
        except AttributeError:
            self.span_context = self.span_id
            tls.span_context = self.span_context
        tls.span_parent = self.span_id
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global spans
        if not self.is_sampled:
            return
        if exc_type:
            self.error_code = ERR_UNKNOWN
            self.error_text = str(exc_val).strip("\t").replace("\t", " ")
        self.duration = int((time.time() - self.start) * US)
        lt = time.localtime(self.start)
        row = "\t".join(str(x) for x in [
            time.strftime("%Y-%m-%d", lt),
            time.strftime("%Y-%m-%d %H:%M:%S", lt),
            self.span_context,
            self.span_id,
            self.parent,
            self.server,
            self.service,
            self.client,
            self.duration,
            self.error_code,
            self.error_text,
            self.sample,
            self.in_label,
            self.out_label
        ])
        with span_lock:
            spans += [row]
        if self.span_parent == DEFAULT_ID:
            del tls.span_parent
            del tls.span_context
        else:
            tls.span_parent = self.span_parent
        metrics["spans"] += 1


def get_spans():
    """
    Get and flush all spans
    :return:
    """
    global spans

    with span_lock:
        r = spans
        spans = []
    return r
