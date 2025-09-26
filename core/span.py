# ----------------------------------------------------------------------
# External call spans
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import threading
import time
from time import perf_counter
import random
import os
import struct
import logging
import uuid
from collections import namedtuple
from contextvars import ContextVar
from typing import Optional, Dict

# NOC modules
from noc.core.error import NO_ERROR, ERR_UNKNOWN
from noc.core.perf import metrics
from noc.core.comp import DEFAULT_ENCODING
from noc.config import config

forensic_logger = logging.getLogger("noc.core.forensic")

SpanItemFields = [
    "date",
    "ts",
    "ctx",
    "id",
    "parent",
    "server",
    "service",
    "client",
    "duration",
    "error_code",
    "error_text",
    "sample",
    "in_label",
    "out_label",
    "in_headers",
]
SpanItem = namedtuple("SpanItem", SpanItemFields)
# Collected spans, protected by lock
span_lock = threading.Lock()
cv_span_context: ContextVar[Optional[int]] = ContextVar("cv_span_context", default=None)
cv_span_parent: ContextVar[Optional[int]] = ContextVar("cv_span_parent", default=None)
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
    def __init__(
        self,
        client=DEFAULT_CLIENT,
        server=DEFAULT_SERVER,
        service=DEFAULT_SERVICE,
        sample=PARENT_SAMPLE,
        in_label=DEFAULT_LABEL,
        parent=DEFAULT_ID,
        context=DEFAULT_ID,
        hist=None,
        quantile=None,
        headers: Optional[Dict[str, bytes]] = None,
        suppress_trace=False,
    ):
        self.client = client
        self.server = server
        self.service = service
        self.sample = sample
        if not sample:
            self.is_sampled = False
        elif sample == DEFAULT_SAMPLE_RATE:
            self.is_sampled = True
        elif sample == PARENT_SAMPLE:
            self.is_sampled = cv_span_context.get() is not None
        else:
            self.is_sampled = random.randint(0, sample - 1) == 0
        self.start = None
        self.duration = None
        self.error_code = NO_ERROR
        self.error_text = DEFAULT_ERROR_TEXT
        self.in_label = in_label
        self.headers = headers or {}
        self.out_label = DEFAULT_LABEL
        self.parent = parent
        self.context = context
        self.span_id = DEFAULT_ID
        self.span_context = DEFAULT_ID
        self.span_parent = DEFAULT_ID
        if config.features.forensic:
            self.forensic_id = str(uuid.uuid4())
        self.hist = hist
        self.quantile = quantile
        self.suppress_trace = suppress_trace

    def __enter__(self):
        if config.features.forensic:
            forensic_logger.info(
                "[>%s|%s|%s] %s", self.forensic_id, self.server, self.service, self.in_label
            )
        if self.is_sampled or self.hist or self.quantile:
            self.ts0 = perf_counter()
        if not self.is_sampled:
            return self
        # Generate span ID
        self.span_id = struct.unpack("!Q", os.urandom(8))[0] & 0x7FFFFFFFFFFFFFFF
        # Get span context
        if cv_span_context.get() is not None:
            self.span_context = cv_span_context.get()
            # Get parent
            if cv_span_parent.get() is not None:
                self.span_parent = cv_span_parent.get()
                if self.parent == DEFAULT_ID:
                    self.parent = self.span_parent
        else:
            self.span_context = self.context if self.context else self.span_id
            cv_span_context.set(self.span_context)
        cv_span_parent.set(self.span_id)
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        global spans
        if self.is_sampled or self.hist or self.quantile:
            self.duration = int((perf_counter() - self.ts0) * US)
        if self.hist:
            self.hist.register(self.duration)
        if self.quantile:
            self.quantile.register(self.duration)
        if config.features.forensic and hasattr(self, "forensic_id"):
            # N.B. config.features.forensic may be changed during span
            forensic_logger.info("[<%s]", self.forensic_id)
        if not self.is_sampled:
            return None
        if exc_type and not self.error_text:
            self.error_code = ERR_UNKNOWN
            self.error_text = str(exc_val).strip("\t").replace("\t", " ").replace("\n", " ")
        lt = time.localtime(self.start)
        ft = time.strftime("%Y-%m-%d %H:%M:%S", lt)
        span = SpanItem(
            date=ft.split(" ")[0],
            ts=ft,
            ctx=self.span_context,
            id=self.span_id,
            parent=self.parent,
            server=str(self.server or ""),
            service=str(self.service or ""),
            client=str(self.client or ""),
            duration=self.duration,
            error_code=self.error_code or 0,
            error_text=str(self.error_text or ""),
            sample=self.sample,
            in_label=str(self.in_label or ""),
            out_label=str(self.out_label or ""),
            in_headers={k: v.decode(DEFAULT_ENCODING) for k, v in self.headers.items()},
        )
        with span_lock:
            spans += [span]
        if self.span_parent == DEFAULT_ID:
            cv_span_parent.set(None)
            cv_span_context.set(None)
        else:
            cv_span_parent.set(self.span_parent)
        metrics["spans"] += 1
        if self.suppress_trace:
            return True

    def set_error(self, code: Optional[int] = None, text: Optional[str] = None) -> None:
        """
        Set error result and code for current span
        :param code: Optional error code
        :param text: Optional error text
        :return:
        """
        if code is not None:
            self.error_code = code
        if text is not None:
            self.error_text = text

    def set_error_from_exc(self, exc: Exception, code: Optional[int] = ERR_UNKNOWN) -> None:
        """
        Set error result and code for current span from exception
        :param exc: Raised exception
        :param code: Optional error code
        :return:
        """
        self.set_error(code=code, text=str(exc))


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


def span_to_dict(span):
    """
    Convert span to object
    :param span:
    :return:
    """
    return dict(zip(SpanItemFields, span))


def get_current_span():
    """
    Get current span if active

    :return: Current context, span
    """
    return cv_span_context.get(), cv_span_parent.get()
