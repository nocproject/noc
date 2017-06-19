# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CLI Errors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------


class CLIError(Exception):
    msg = "Unspecified CLI error"


class CLIAuthFailed(CLIError):
    msg = "Authentication failed"


class CLINoSuperCommand(CLIError):
    msg = "No super command defined"


class CLILowPrivileges(CLIError):
    msg = "No super privileges"


class CLISSHProtocolError(CLIError):
    msg = "SSH Protocol error"
