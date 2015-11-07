# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Deferred calls
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.scheduler.job import Job


def call_later(name, delay=None, **kwargs):
    """
    Run callable *name* in scheduler process
    :param name: Full callable name
    :param delay: delay in seconds
    """
    Job.submit(
        "scheduler",
        "noc.core.scheduler.calljob.CallJob",
        key=name,
        data=kwargs,
        delta=delay
    )
