# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Script errors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


class ScriptError(Exception):
    msg = "Script error"


class CLISyntaxError(ScriptError):
    msg = "Syntax error"


class CLIOperationError(ScriptError):
    msg = "Operational CLI error"


class NotSupportedError(ScriptError):
    msg = "Feature is not supported"


class UnexpectedResultError(ScriptError):
    msg = "Unexpected result"
