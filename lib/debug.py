# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Various debugging and error logging utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import sys
import re
import logging
import datetime
import os
import stat
import hashlib
import pprint
import traceback
import uuid
## NOC modules
from noc.settings import TRACEBACK_REVERSE
from noc.lib.version import get_branch, get_tip
from noc.lib.fileutils import safe_rewrite
from noc.lib.serialize import json_encode

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig()


# CP error reporting
ENABLE_CP = True
CP_NEW = "var/cp/crashinfo/new"
CP_SET_UID = None

if os.getuid() == 0:
    CP_SET_UID = os.stat("local")[stat.ST_UID]

if not os.path.isdir(CP_NEW):
    try:
        os.makedirs(CP_NEW, 0700)
    except OSError, why:
        logger.error("Cannot initialize CP reporting: %s", why)
        ENABLE_CP = False
    if CP_SET_UID:
        try:
            os.chown(CP_NEW, CP_SET_UID, -1)
        except OSError, why:
            logger.error("Cannot initialize CP reporting: %s", why)
            ENABLE_CP = False


def get_lines_from_file(filename, lineno, context_lines,
                        loader=None, module_name=None):
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
    encoding = "ascii"
    for line in source[:2]:
        # File coding may be specified. Match pattern from PEP-263
        # (http://www.python.org/dev/peps/pep-0263/)
        match = re.search(r"coding[:=]\s*([-\w.]+)", line)
        if match:
            encoding = match.group(1)
            break
    source = [unicode(sline, encoding, "replace") for sline in source]
    lower_bound = max(0, lineno - context_lines)
    upper_bound = lineno + context_lines
    pre_context = [line.strip("\n") for line in source[lower_bound:lineno]]
    context_line = source[lineno].strip("\n")
    post_context = [line.strip("\n")
                    for line in source[lineno + 1:upper_bound]]
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
        pre_context_lineno, pre_context, context_line,\
        post_context = get_lines_from_file(filename, lineno, 7,
                                           loader, module_name)
        if pre_context_lineno is not None:
            frames += [{
                "tb": tb,
                "filename": filename,
                "function": function,
                "lineno": lineno + 1,
                "vars": tb.tb_frame.f_locals.items(),
                "id": id(tb),
                "pre_context": pre_context,
                "context_line": context_line,
                "post_context": post_context,
                "pre_context_lineno": pre_context_lineno + 1
            }]
        tb = tb.tb_next
    if not frames:
        frames = [{
            "filename": "unknown",
            "function": "?",
            "lineno": "?",
            "context_line": "???"
        }]
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
        pre_context_lineno, pre_context, context_line,\
        post_context = get_lines_from_file(filename, lineno, 7,
                                           loader, module_name)
        if pre_context_lineno is not None:
            frames += [{
                "filename": filename,
                "function": function,
                "lineno": lineno + 1,
                "vars": frame.f_locals.items(),
                "pre_context": pre_context,
                "context_line": context_line,
                "post_context": post_context,
                "pre_context_lineno": pre_context_lineno + 1,
            }]
    if not frames:
        frames = [{
            "filename": "unknown",
            "function": "?",
            "lineno": "?",
            "context_line": "???"
        }]
    return frames


def format_frames(frames, reverse=TRACEBACK_REVERSE):
    def format_source(lineno, lines):
        r = []
        for l in lines:
            r += ["%5d     %s" % (lineno, l)]
            lineno += 1
        return "\n".join(r)

    r = []
    r += [u"START OF TRACEBACK"]
    r += [u"-" * 72]
    fr = frames[:]
    if reverse:
        fr.reverse()
    for f in fr:
        r += [u"File: %s (Line: %s)" % (os.path.relpath(f["filename"]), f["lineno"])]
        r += [u"Function: %s" % (f["function"])]
        if "pre_context_lineno" in f:
            r += [format_source(f["pre_context_lineno"], f["pre_context"])]
            r += [u"%5d ==> %s" % (f["lineno"], f["context_line"])]
            r += [format_source(f["lineno"] + 1, f["post_context"])]
            r += [u"Variables:"]
            for n, v in f["vars"]:
                try:
                    pv = unicode(repr(v), "utf-8")
                    if len(pv) > 72:
                        pv = u"\n" + pprint.pformat(v)
                except:
                    pv = u"repr() failed"
                r += [u"%20s = %s" % (n, pv)]
        else:
            r += ["???"]
        r += [u"-" * 72]
    r += [u"END OF TRACEBACK"]
    return u"\n".join(r)


def check_fatal_errors(t, v):
    def die(msg, *args, **kwargs):
        logger.error(msg, *args, **kwargs)
        os._exit(1)

    xn = "%s.%s" % (t.__module__, t.__name__)
    if xn == "pymongo.errors.AutoReconnect":
        die("Failed to connect MongoDB: %s", v)
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


def get_traceback(reverse=TRACEBACK_REVERSE, fp=None):
    t, v, tb = sys.exc_info()
    try:
        check_fatal_errors(t, v)
    except:
        pass  # Ignore exceptions
    now = datetime.datetime.now()
    try:
        branch = get_branch()
        tip = get_tip()
    except:
        # We cannot get branch and tip on "Too many open files" error
        branch = "unknown"
        tip = "unknown"
    r = [
        "UNHANDLED EXCEPTION (%s)" % str(now),
        "BRANCH: %s TIP: %s" % (branch, tip),
        "PROCESS: %s" % sys.argv[0]
    ]
    if fp:
        r += ["ERROR FINGERPRINT: %s" % fp]
    r += [
        "WORKING DIRECTORY: %s" % os.getcwd(),
        "EXCEPTION: %s %s" % (t, v),
        format_frames(get_traceback_frames(tb), reverse=reverse)
    ]
    if not reverse:
        r += [
            "UNHANDLED EXCEPTION (%s)" % str(now),
            str(t),
            str(v)
        ]
    return "\n".join(r)


def excepthook(t, v, tb):
    """
    Override default exception handler
    """
    now = datetime.datetime.now()
    r = ["UNHANDLED EXCEPTION (%s)" % str(now)]
    r += ["Working directory: %s" % os.getcwd()]
    r += [str(t), str(v)]
    r += [format_frames(get_traceback_frames(tb))]
    sys.stdout.write("\n".join(r))
    sys.stdout.flush()


def error_report(reverse=TRACEBACK_REVERSE, logger=logger):
    fp = error_fingerprint()
    r = get_traceback(reverse=reverse, fp=fp)
    logger.error(r)
    if ENABLE_CP:
        fp = error_fingerprint()
        path = os.path.join(CP_NEW, fp + ".json")
        if not os.path.exists(path):
            # @todo: TZ
            # @todo: Installation ID
            c = {
                "ts": datetime.datetime.now().isoformat(),
                "uuid": fp,
                # "installation": None,
                "process": os.path.relpath(sys.argv[0]),
                "branch": get_branch(),
                "tip": get_tip(),
                "traceback": r
            }
            try:
                safe_rewrite(path, json_encode(c))
                if CP_SET_UID:
                    os.chown(path, CP_SET_UID, -1)
                logger.error("Writing CP report to %s", path)
            except OSError, why:
                logger.error("Unable to write CP report: %s", why)
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
        if not (tb_file.startswith("..") or
                    tb_file.startswith("lib/python")):
            noc_file = tb_file
            noc_function = tb_function
            noc_lineno = tb_lineno
        tb = tb.tb_next
    parts = [
        get_branch(),
        os.path.relpath(sys.argv[0]),  # Process
        str(t),  # Exception class
        noc_file, noc_function, str(noc_lineno),  # NOC code point
        tb_file, tb_function, str(tb_lineno)  # Absolute code point
    ]
    hash = hashlib.sha1("|".join(p if p else "" for p in parts)).digest()
    return str(uuid.UUID(bytes=hash[:16], version=5))


def dump_stacks():
    """
    Dump all active threads' stacks
    """
    for tid, stack in sys._current_frames().items():
        print "[THREAD #%s]" % tid
        for filename, lineno, name, line in traceback.extract_stack(stack):
            print "File: '%s', line %d, in %s" % (filename, lineno, name)
            if line:
                print "    %s" % line.strip()


def BQ(s):
    """
    Pretty-format binary string
    :param s: String to format
    :return: Formatted string

    >>> BQ("test")
    u'test'
    >>> BQ("\\xa8\\xf9\\x80")
    '(A8 F9 80)'
    """
    try:
        return unicode(s)
    except UnicodeDecodeError:
        return "(%s)" % " ".join(["%02X" % ord(c) for c in s])
