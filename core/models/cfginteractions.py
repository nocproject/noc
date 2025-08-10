# ---------------------------------------------------------------------
# Interaction Audit
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
from collections import namedtuple
import enum

# NOC modules
from noc.config import config

TTL_COMMAND = config.audit.command_ttl
TTL_LOGIN = config.audit.login_ttl
TTL_REBOOT = config.audit.reboot_ttl
TTL_CONFIG = config.audit.config_changed_ttl

InteractionSetting = namedtuple("InteractionSetting", ["ttl", "text"])


CONFIGS = {
    0: InteractionSetting(ttl=TTL_COMMAND, text=""),
    1: InteractionSetting(ttl=TTL_LOGIN, text="User logged in"),
    2: InteractionSetting(ttl=TTL_LOGIN, text="User logged out"),
    3: InteractionSetting(ttl=TTL_REBOOT, text="System rebooted"),
    4: InteractionSetting(ttl=TTL_REBOOT, text="System started"),
    5: InteractionSetting(ttl=TTL_REBOOT, text="System halted"),
    6: InteractionSetting(ttl=TTL_CONFIG, text="Config changed"),
}


class Interaction(enum.Enum):
    @property
    def config(self):
        return CONFIGS[self.value]

    OP_COMMAND = 0
    OP_LOGIN = 1
    OP_LOGOUT = 2
    OP_REBOOT = 3
    OP_STARTED = 4
    OP_HALTED = 5
    OP_CONFIG_CHANGED = 6
