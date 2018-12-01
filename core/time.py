# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# perf_counter backport
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import ctypes
import errno
from ctypes.util import find_library
import os
import time

_platform = os.uname()[0].lower()

if _platform == "linux":
    CLOCK_MONOTONIC_RAW = 4
elif _platform == "freebsd":
    CLOCK_MONOTONIC_RAW = 4
else:
    CLOCK_MONOTONIC_RAW = None

if CLOCK_MONOTONIC_RAW is None:
    # Fallback
    perf_counter = time.time
else:
    # High-resolution timer
    clockid_t = ctypes.c_int
    time_t = ctypes.c_long

    class timespec(ctypes.Structure):
        _fields_ = [
            ("tv_sec", time_t),  # seconds
            ("tv_nsec", ctypes.c_long)  # nanoseconds
        ]
    _clock_gettime = ctypes.CDLL(find_library('rt'), use_errno=True).clock_gettime
    _clock_gettime.argtypes = [clockid_t, ctypes.POINTER(timespec)]

    def perf_counter():
        tp = timespec()
        if _clock_gettime(CLOCK_MONOTONIC_RAW, ctypes.byref(tp)) < 0:
            err = ctypes.get_errno()
            msg = errno.errorcode[err]
            if err == errno.EINVAL:
                msg += " Unsupported clk_id: %s" % CLOCK_MONOTONIC_RAW
            raise OSError(err, msg)
        return tp.tv_sec + tp.tv_nsec * 1e-9
