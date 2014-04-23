# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Various debugging and error logging utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import sys
import re
import logging
import datetime
import os
import cPickle
import time
import stat
import hashlib
import pprint
## NOC modules
from noc.settings import CRASHINFO_LIMIT, TRACEBACK_REVERSE
from noc.lib.version import get_version
from noc.lib.fileutils import safe_rewrite

#
# Error reporting context
#
DEBUG_CTX_COMPONENT = None
DEBUG_CTX_CRASH_DIR = None
DEBUG_CTX_CRASH_PREFIX = "crashinfo-"
DEBUG_CTX_SET_UID = None


def set_crashinfo_context(component, crash_dir):
    global DEBUG_CTX_COMPONENT, DEBUG_CTX_CRASH_DIR, DEBUG_CTX_SET_UID
    DEBUG_CTX_COMPONENT = component
    DEBUG_CTX_CRASH_DIR = crash_dir
    if os.getuid() == 0:  # Daemon launched as a root
        DEBUG_CTX_SET_UID = os.stat(crash_dir)[stat.ST_UID]


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
                    "context_line": "???",
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
        r += [u"File: %s (Line: %s)" % (f["filename"], f["lineno"])]
        r += [u"Function: %s" % (f["function"])]
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
        r += [u"-" * 72]
    r += [u"END OF TRACEBACK"]
    return u"\n".join(r)


def get_traceback(reverse=TRACEBACK_REVERSE):
    t, v, tb = sys.exc_info()
    now = datetime.datetime.now()
    r = ["UNHANDLED EXCEPTION (%s)" % str(now)]
    r += ["Working directory: %s" % os.getcwd()]
    r += [str(t), str(v)]
    r += [format_frames(get_traceback_frames(tb), reverse=reverse)]
    if not reverse:
        r += ["UNHANDLED EXCEPTION (%s)" % str(now)]
        r += [str(t), str(v)]
    return "\n".join(r)


def error_report(reverse=TRACEBACK_REVERSE):
    r = get_traceback(reverse=reverse)
    logging.error(r)
    if DEBUG_CTX_COMPONENT and DEBUG_CTX_CRASH_DIR:
        # Build crashinfo file
        c = {
            "source": "system",
            "type": "Unhandled Exception",
            "ts": int(time.time()),
            "component": DEBUG_CTX_COMPONENT,
            "traceback": r,
        }
        crashinfo = cPickle.dumps(c)
        # Check crashinfo is inside limits
        if len(crashinfo) > CRASHINFO_LIMIT:
            return
        # Write crashinfo
        fp = error_fingerprint()
        path = os.path.join(DEBUG_CTX_CRASH_DIR, DEBUG_CTX_CRASH_PREFIX + fp)
        try:
            safe_rewrite(path, crashinfo)
            if DEBUG_CTX_SET_UID:  # Change crashinfo userid to directory"s owner
                os.chown(path, DEBUG_CTX_SET_UID, -1)
        except OSError, why:
            logging.error("Unable to write crashinfo: %s" % why)


def frame_report(frame, caption=None):
    now = datetime.datetime.now()
    r = []
    if caption:
        r += [caption]
    r += ["EXECUTION FRAME REPORT (%s)" % str(now)]
    r += ["Working directory: %s" % os.getcwd()]
    r += [format_frames(get_execution_frames(frame))]
    logging.error("\n".join(r))


def error_fingerprint():
    """
    Generate error fingerprint.
    :return:
    """
    tb = sys.exc_info()[2]
    # Generate fingerprint seed
    s = ":".join([str(x) for x in [
            DEBUG_CTX_COMPONENT,  # Component
            get_version(),  # NOC version
            tb.tb_frame.f_code.co_filename,  # Filename
            tb.tb_frame.f_globals.get("__name__"),  # Module
            tb.tb_frame.f_code.co_name,  # Function
            tb.tb_lineno - 1  # Line
        ]
    ])
    return hashlib.sha1(s).hexdigest()


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
