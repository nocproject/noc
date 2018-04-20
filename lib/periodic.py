# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Periodic Task base class
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import os
import datetime
import logging
# NOC modules
=======
##----------------------------------------------------------------------
## Periodic Task base class
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import os
import datetime
import logging
## NOC modules
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
from noc.lib.registry import Registry


class PeriodicRegistry(Registry):
    """Registry for all periodic tasks"""
    name = "PeriodicRegistry"
    subdir = "periodics"
    classname = "Task"

periodic_registry = PeriodicRegistry()


class TaskBase(type):
    """Metaclass for Task"""
    def __new__(cls, name, bases, attrs):
        m = type.__new__(cls, name, bases, attrs)
        periodic_registry.register(m.name, m)
        return m
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

class Task(object):
    """Task handler"""
    __metaclass__ = TaskBase
    name = None
    description = ""
    # A list of periodic task names which cannot be started concurrenctly
    wait_for = []
    # Default task timeout.
    # If set to None, task has no configurable timeout,
    # Otherwise it can be configured
    default_timeout = None
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def __init__(self, timeout=None):
        if self.default_timeout:
            self.timeout = timeout if timeout else self.default_timeout
        else:
            self.timeout = None
<<<<<<< HEAD

=======
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def execute(self):
        return True

    def debug(self, msg):
        logging.debug("%s: %s" % (self.name, msg))

    def info(self, msg):
        logging.info("%s: %s" % (self.name, msg))

    def error(self, msg):
        logging.error("%s: %s" % (self.name, msg))
