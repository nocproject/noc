# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Discovery handlers
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from noc.config import config

DELAY = config.correlator.discovery_delay
=======
##----------------------------------------------------------------------
## Discovery handlers
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.inv.discovery.scheduler import DiscoveryScheduler

DELAY = 600
discovery_scheduler = DiscoveryScheduler()

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

def schedule_discovery(event):
    """
    Reschedule discovery processes
    """
<<<<<<< HEAD
=======
    # Check managed object is managed
    if not event.managed_object.is_managed:
        return
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    event.managed_object.run_discovery(DELAY)
