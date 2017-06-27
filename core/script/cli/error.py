# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# CLI Errors
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.error import (
    NOCError, ERR_CLI_UNKNOWN, ERR_CLI_AUTH_FAILED,
    ERR_CLI_NO_SUPER_COMMAND, ERR_CLI_LOW_PRIVILEGES,
    ERR_CLI_SSH_PROTOCOL_ERROR, ERR_CLI_CONNECTION_REFUSED)


class CLIError(NOCError):
    default_code = ERR_CLI_UNKNOWN
    default_msg = "Unspecified CLI error"


class CLIConnectionRefused(CLIError):
    default_code = ERR_CLI_CONNECTION_REFUSED
    default_msg = "Connection refused"


class CLIAuthFailed(CLIError):
    default_code = ERR_CLI_AUTH_FAILED
    default_msg = "Authentication failed"


class CLINoSuperCommand(CLIError):
    default_code = ERR_CLI_NO_SUPER_COMMAND
    default_msg = "No super command defined"


class CLILowPrivileges(CLIError):
    default_code = ERR_CLI_LOW_PRIVILEGES
    default_msg = "No super privileges"


class CLISSHProtocolError(CLIError):
    default_code = ERR_CLI_SSH_PROTOCOL_ERROR
    default_msg = "SSH Protocol error"
