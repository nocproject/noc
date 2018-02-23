# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# External call spans
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import threading
import time
import random
import os
import struct
import logging
import uuid
# Third-party modules
import tornado.gen
# NOC modules
from noc.core.error import NO_ERROR, ERR_UNKNOWN
from noc.core.perf import metrics
from noc.config import config

forensic_logger = logging.getLogger("noc.core.forensic")
span_lock = threading.Lock()

# Collected spans, protected by lock
SPAN_FIELDS = "span.date.ts.ctx.id.parent.server.service.client" \
              ".duration.error_code.error_text.sample" \
              ".in_label.out_label"
tls = threading.local()
spans = []

DEFAULT_CLIENT = "NOC"
DEFAULT_SERVER = "NOC"
DEFAULT_SERVICE = "unknown"
DEFAULT_SAMPLE_RATE = 1
PARENT_SAMPLE = -1
DEFAULT_ERROR_TEXT = ""
DEFAULT_LABEL = ""
DEFAULT_ID = 0
US = 1000000.0


class Span(object):
    def __init__(self, client=DEFAULT_CLIENT, server=DEFAULT_SERVER,
                 service=DEFAULT_SERVICE, sample=PARENT_SAMPLE,
                 in_label=DEFAULT_LABEL, parent=DEFAULT_ID,
                 context=DEFAULT_ID):
        self.client = client
        self.server = server
        self.service = service
        self.sample = sample
        if not sample:
            self.is_sampled = False
        elif sample == DEFAULT_SAMPLE_RATE:
            self.is_sampled = True
        elif sample == PARENT_SAMPLE:
            self.is_sampled = hasattr(tls, "span_context")
        else:
            self.is_sampled = random.randint(0, sample - 1) == 0
        self.start = None
        self.duration = None
        self.error_code = NO_ERROR
        self.error_text = DEFAULT_ERROR_TEXT
        self.in_label = in_label
        self.out_label = DEFAULT_LABEL
        self.parent = parent
        self.context = context
        self.span_id = DEFAULT_ID
        self.span_context = DEFAULT_ID
        self.span_parent = DEFAULT_ID
        if config.features.forensic:
            self.forensic_id = str(uuid.uuid4())

    def __enter__(self):
        if config.features.forensic:
            forensic_logger.info(
                "[>%s|%s|%s] %s",
                self.forensic_id, self.server,
                self.service, self.in_label
            )
        if not self.is_sampled:
            return self
        # Generate span ID
        self.span_id = struct.unpack("!Q", os.urandom(8))[0] & 0x7fffffffffffffff
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
            self.span_context = self.context if self.context else self.span_id
            tls.span_context = self.span_context
        tls.span_parent = self.span_id
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        def q_tsv(s):
            if not s:
                return ""
            else:
                return str(s).encode("string_escape")

        global spans
        if config.features.forensic and hasattr(self, "forensic_id"):
            # N.B. config.features.forensic may be changed during span
            forensic_logger.info("[<%s]", self.forensic_id)
        if not self.is_sampled:
            return
        if exc_type and not self.error_text and not self.is_ignorable_error(exc_type):
            self.error_code = ERR_UNKNOWN
            self.error_text = str(exc_val).strip("\t").replace("\t", " ").replace("\n", " ")
        self.duration = int((time.time() - self.start) * US)
        lt = time.localtime(self.start)
        row = "\t".join(str(x) for x in [
            time.strftime("%Y-%m-%d", lt),
            time.strftime("%Y-%m-%d %H:%M:%S", lt),
            self.span_context,
            self.span_id,
            self.parent,
            q_tsv(self.server),
            q_tsv(self.service),
            q_tsv(self.client),
            self.duration,
            self.error_code or 0,
            q_tsv(self.error_text),
            self.sample,
            q_tsv(self.in_label),
            q_tsv(self.out_label)
        ])
        with span_lock:
            spans += [row]
        if self.span_parent == DEFAULT_ID:
            del tls.span_parent
            del tls.span_context
        else:
            tls.span_parent = self.span_parent
        metrics["spans"] += 1

    @staticmethod
    def is_ignorable_error(exc_type):
        return exc_type == tornado.gen.Return


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


def get_current_span():
    """
    Get current span if active

    :return: Current context, span or None, None
    """
    return getattr(tls, "span_context", None), getattr(tls, "span_parent", None)
