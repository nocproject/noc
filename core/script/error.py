# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Script errors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.error import (
    NOCError, ERR_SCRIPT_UNKNOWN, ERR_SCRIPT_SYNTAX,
    ERR_SCRIPT_OPERATION, ERR_SCRIPT_NOT_SUPPORTED,
    ERR_SCRIPT_UNEXPECTED_RESULT)


class ScriptError(NOCError):
    default_msg = "Script error"
    default_code = ERR_SCRIPT_UNKNOWN


class CLISyntaxError(ScriptError):
    default_msg = "Syntax error"
    default_code = ERR_SCRIPT_SYNTAX


class CLIOperationError(ScriptError):
    default_msg = "Operational CLI error"
    default_code = ERR_SCRIPT_OPERATION


class NotSupportedError(ScriptError):
    default_msg = "Feature is not supported"
    default_code = ERR_SCRIPT_NOT_SUPPORTED


class UnexpectedResultError(ScriptError):
    default_msg = "Unexpected result"
    default_code = ERR_SCRIPT_UNEXPECTED_RESULT
