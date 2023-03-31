# ----------------------------------------------------------------------
# System interactions
# ----------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from typing import Set
from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class InteractionConfig(object):
    models: Set[str]
    description: str = ""


CONFIGS = {
    "SA": InteractionConfig(models={"sa.ManagedObject"}),
    "ALARM": InteractionConfig(models={"sa.ManagedObject"}),
    "EVENT": InteractionConfig(models={"sa.ManagedObject"}),
    "TT": InteractionConfig(models={"sa.ManagedObject"}),
    "BOX": InteractionConfig(models={"sa.ManagedObject"}),
    "PERIODIC": InteractionConfig(models={"sa.ManagedObject"}),
    "A_CONFIG": InteractionConfig(models={"pm.Agent"}),
    "A_REGISTER": InteractionConfig(models={"pm.Agent"}),
}


class Interaction(str, Enum):
    @property
    def config(self):
        return CONFIGS[self.value]

    ServiceActivation = "SA"  # Allow system active login with device
    Alarm = "ALARM"  # Allow system Raise alarm for source
    Event = "EVENT"  # Allow processed Events for source
    Escalation = "TT"  # Allow Sent Alarm as TT to external system
    BoxDiscovery = "BOX"  # Box Discovery
    PeriodicDiscovery = "PERIODIC"  # Periodic Discovery
    AgentConfig = "A_CONFIG"
    AgentRegister = "A_REGISTER"
