# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Various debugging and error logging utilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import print_function
import sys
import re
import logging
import datetime
import os
import hashlib
import pprint
import traceback
import uuid

# Third-party modules
import six
import ujson

# NOC modules
from noc.config import config
from noc.core.version import version
from noc.core.fileutils import safe_rewrite
from noc.core.perf import metrics
from noc.core.comp import smart_bytes, smart_text

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig()

rx_coding = re.compile(r"coding[:=]\s*([-\w.]+)")

# CP error reporting
ENABLE_CP = config.features.cp
CP_NEW = config.path.cp_new
CP_SET_UID = None

SERVICE_NAME = os.path.relpath(sys.argv[0] or sys.executable)

# Sentry error reporting
if config.features.sentry:
    from raven import Client as RavenClient

    raven_client = RavenClient(
        config.sentry.url,
        processors=("raven.processors.SanitizePasswordsProcessor",),
        release=version.version,
    )


def get_lines_from_file(filename, lineno, context_lines, loader=None, module_name=None):
    """
    Returns context_lines before and after lineno from file.
    Returns (pre_context_lineno, pre_context, context_line, post_context).
    (Borrowed from Django)
    """
    source = None
    if loader is not None and hasattr(loader, "get_source"):
        source = loader.get_source(module_name)
        if source is not None:
            source = source.splitlines()
    if source is None:
        try:
            f = open(filename)
            try:
                source = f.readlines()
            finally:
                f.close()
        except (OSError, IOError):
            pass
    if source is None:
        return None, [], None, []
    source = [smart_text(sline) for sline in source]
    lower_bound = max(0, lineno - context_lines)
    upper_bound = lineno + context_lines
    pre_context = [line.strip("\n") for line in source[lower_bound:lineno]]
    context_line = source[lineno].strip("\n")
    post_context = [line.strip("\n") for line in source[lineno + 1 : upper_bound]]
    return lower_bound, pre_context, context_line, post_context


def get_traceback_frames(tb):
    """
    (Borrowed from django)
    """
    frames = []
    while tb is not None:
        # support for __traceback_hide__ which is used by a few libraries
        # to hide internal frames.
        if tb.tb_frame.f_locals.get("__traceback_hide__"):
            tb = tb.tb_next
            continue
        filename = tb.tb_frame.f_code.co_filename
        function = tb.tb_frame.f_code.co_name
        lineno = tb.tb_lineno - 1
        loader = tb.tb_frame.f_globals.get("__loader__")
        module_name = tb.tb_frame.f_globals.get("__name__")
        pre_context_lineno, pre_context, context_line, post_context = get_lines_from_file(
            filename, lineno, 7, loader, module_name
        )
        if pre_context_lineno is not None:
            frames += [
                {
                    "tb": tb,
                    "filename": filename,
                    "function": function,
                    "lineno": lineno + 1,
                    "vars": six.iteritems(tb.tb_frame.f_locals),
                    "id": id(tb),
                    "pre_context": pre_context,
                    "context_line": context_line,
                    "post_context": post_context,
                    "pre_context_lineno": pre_context_lineno + 1,
                }
            ]
        tb = tb.tb_next
    if not frames:
        frames = [{"filename": "unknown", "function": "?", "lineno": "?", "context_line": "???"}]
    return frames


def get_execution_frames(frame):
    e_f = []
    while frame is not None:
        e_f += [frame]
        frame = frame.f_back
    e_f.reverse()
    frames = []
    for frame in e_f:
        filename = frame.f_code.co_filename
        function = frame.f_code.co_name
        lineno = frame.f_lineno - 1
        loader = frame.f_globals.get("__loader__")
        module_name = frame.f_globals.get("__name__")
        pre_context_lineno, pre_context, context_line, post_context = get_lines_from_file(
            filename, lineno, 7, loader, module_name
        )
        if pre_context_lineno is not None:
            frames += [
                {
                    "filename": filename,
                    "function": function,
                    "lineno": lineno + 1,
                    "vars": six.iteritems(frame.f_locals),
                    "pre_context": pre_context,
                    "context_line": context_line,
                    "post_context": post_context,
                    "pre_context_lineno": pre_context_lineno + 1,
                }
            ]
    if not frames:
        frames = [{"filename": "unknown", "function": "?", "lineno": "?", "context_line": "???"}]
    return frames


def format_frames(frames, reverse=config.traceback.reverse):
    def format_source(lineno, lines):
        r = []
        for l in lines:
            r += ["%5d     %s" % (lineno, l)]
            lineno += 1
        return "\n".join(r)

    r = []
    r += ["START OF TRACEBACK"]
    r += ["-" * 72]
    fr = frames[:]
    if reverse:
        fr.reverse()
    for f in fr:
        r += ["File: %s (Line: %s)" % (os.path.relpath(f["filename"]), f["lineno"])]
        r += ["Function: %s" % (f["function"])]
        if "pre_context_lineno" in f:
            r += [format_source(f["pre_context_lineno"], f["pre_context"])]
            r += ["%5d ==> %s" % (f["lineno"], f["context_line"])]
            r += [format_source(f["lineno"] + 1, f["post_context"])]
            r += ["Variables:"]
            for n, v in f["vars"]:
                try:
                    pv = smart_text(repr(v))
                    if len(pv) > 72:
                        pv = "\n" + pprint.pformat(v)
                except:  # noqa
                    pv = "repr() failed"
                r += ["%20s = %s" % (n, pv)]
        else:
            r += ["???"]
        r += ["-" * 72]
    r += ["END OF TRACEBACK"]
    return "\n".join(r)


def check_fatal_errors(t, v):
    def die(msg, *args, **kwargs):
        logger.error(msg, *args, **kwargs)
        logger.error("Exiting due to fatal error")
        os._exit(1)

    xn = "%s.%s" % (t.__module__, t.__name__)
    if xn == "pymongo.errors.AutoReconnect":
        die("Reconnecting to MongoDB: %s", v)
    elif xn == "pymongo.errors.ServerSelectionTimeoutError":
        die("Cannot select MongoDB master: %s", v)
    elif xn == "django.db.utils.DatabaseError" and "server closed" in v:
        die("Failed to connect PostgreSQL: %s", v)
    elif xn == "psycopg2.InterfaceError" and "connection already closed" in v:
        die("PostgreSQL connection closed: %s", v)
    elif xn == "psycopg2.OperationalError":
        die("PostgreSQL operational error: %s", v)
    elif xn == "django.db.utils.DatabaseError":
        die("PostgreSQL database error: %s", v)
    elif xn == "django.core.exceptions.ImproperlyConfigured":
        die("Improperly configured: %s", v)


def get_traceback(reverse=config.traceback.reverse, fp=None, exc_info=None):
    exc_info = exc_info or sys.exc_info()
    t, v, tb = exc_info
    try:
        check_fatal_errors(t, v)
    except:  # noqa
        pass  # noqa Ignore exceptions
    now = datetime.datetime.now()
    r = [
        "UNHANDLED EXCEPTION (%s)" % str(now),
        "PROCESS: %s" % version.process,
        "VERSION: %s" % version.version,
    ]
    if version.branch:
        r += ["BRANCH: %s CHANGESET: %s" % (version.branch, version.changeset)]
    if fp:
        r += ["ERROR FINGERPRINT: %s" % fp]
    r += [
        "WORKING DIRECTORY: %s" % os.getcwd(),
        "EXCEPTION: %s %s" % (t, v),
        format_frames(get_traceback_frames(tb), reverse=reverse),
    ]
    if not reverse:
        r += ["UNHANDLED EXCEPTION (%s)" % str(now), str(t), str(v)]
    return "\n".join(smart_text(x, "ignore") for x in r)


def excepthook(t, v, tb):
    """
    Override default exception handler
    """
    import datetime  # Required for pytest
    import sys

    now = datetime.datetime.now()
    r = ["UNHANDLED EXCEPTION (%s)" % str(now)]
    r += ["Working directory: %s" % os.getcwd()]
    r += [str(t), str(v)]
    r += [format_frames(get_traceback_frames(tb))]
    sys.stdout.write("\n".join(r))
    sys.stdout.flush()


def error_report(reverse=config.traceback.reverse, logger=logger):
    fp = error_fingerprint()
    r = get_traceback(reverse=reverse, fp=fp)
    logger.error(r)
    metrics["errors"] += 1
    if config.sentry.url:
        try:
            raven_client.captureException(fingerprint=[fp])
        except Exception as e:
            logger.error("Failed to sent problem report to Sentry: %s", e)
    if ENABLE_CP:
        fp = error_fingerprint()
        path = os.path.join(CP_NEW, fp + ".json")
        if os.path.exists(path):
            # Touch file
            os.utime(path, None)
        else:
            metrics["unique_errors"] += 1
            # @todo: TZ
            # @todo: Installation ID
            c = {
                "ts": datetime.datetime.now().isoformat(),
                "uuid": fp,
                # "installation": None,
                "process": SERVICE_NAME,
                "version": version.version,
                "branch": version.branch,
                "tip": version.changeset,
                "changeset": version.changeset,
                "traceback": r,
            }
            try:
                safe_rewrite(path, ujson.dumps(c))
                if CP_SET_UID:
                    os.chown(path, CP_SET_UID, -1)
                logger.error("Writing CP report to %s", path)
            except OSError as e:
                logger.error("Unable to write CP report: %s", e)
    return r


def frame_report(frame, caption=None, logger=logger):
    now = datetime.datetime.now()
    r = []
    if caption:
        r += [caption]
    r += ["EXECUTION FRAME REPORT (%s)" % str(now)]
    r += ["Working directory: %s" % os.getcwd()]
    r += [format_frames(get_execution_frames(frame))]
    logger.error("\n".join(r))


def error_fingerprint():
    t, v, tb = sys.exc_info()
    noc_file = None
    noc_function = None
    noc_lineno = None
    tb_file = None
    tb_function = None
    tb_lineno = None
    while tb is not None:
        # support for __traceback_hide__ which is used by a few libraries
        # to hide internal frames.
        if tb.tb_frame.f_locals.get("__traceback_hide__"):
            tb = tb.tb_next
            continue
        tb_file = os.path.relpath(tb.tb_frame.f_code.co_filename)
        for p in ("python2.6", "python2.7"):
            tb_file = tb_file.replace(p, "python2.X")
        tb_function = tb.tb_frame.f_code.co_name
        tb_lineno = tb.tb_lineno - 1
        if not (tb_file.startswith("..") or tb_file.startswith("lib/python")):
            noc_file = tb_file
            noc_function = tb_function
            noc_lineno = tb_lineno
        tb = tb.tb_next
    parts = [
        version.branch,
        SERVICE_NAME,  # Process
        str(t),  # Exception class
        noc_file,
        noc_function,
        str(noc_lineno),  # NOC code point
        tb_file,
        tb_function,
        str(tb_lineno),  # Absolute code point
    ]
    eh = hashlib.sha1(smart_bytes(b"|".join(smart_bytes(p if p else "") for p in parts))).digest()
    return str(uuid.UUID(bytes=eh[:16], version=5))


def dump_stacks(thread_id=None):
    """
    Dump all or selected active threads' stacks
    """
    for tid, stack in six.iteritems(sys._current_frames()):
        if thread_id and tid != thread_id:
            continue
        print("[THREAD #%s]" % tid)
        for filename, lineno, name, line in traceback.extract_stack(stack):
            print("File: '%s', line %d, in %s" % (filename, lineno, name))
            if line:
                print("    %s" % line.strip())


class ErrorReport(object):
    """
    error_report context wrapper
    """

    def __init__(self, reverse=config.traceback.reverse, logger=logger):
        self.reverse = reverse
        self.logger = logger

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            error_report(self.reverse, self.logger)
