# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Profile loader
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import sys
import glob
import logging
import inspect
import os
import threading
## NOC modules
from base import BaseProfile

logger = logging.getLogger(__name__)


class ProfileLoader(object):
    def __init__(self):
        self.profiles = {}  # Load profiles
        self.lock = threading.Lock()
        self.all_profiles = set()

    def get_profile(self, name):
        """
        Load profile and return BaseProfile instance.
        Returns None when no profile found or loading error occured
        """
        with self.lock:
            profile = self.profiles.get(name)
            if not profile:
                logger.info("Loading profile %s", name)
                if not self.is_valid_name(name):
                    logger.error("Invalid profile name")
                    return None
                module_name = "sa.profiles.%s" % name
                try:
                    sm = __import__(module_name, {}, {}, "*")
                    for n in dir(sm):
                        o = getattr(sm, n)
                        if (
                            inspect.isclass(o) and
                            issubclass(o, BaseProfile) and
                            o.__module__ == sm.__name__
                        ):
                            profile = o
                            break
                    if not profile:
                        logger.error("Profile not found: %s", name)
                except Exception, why:
                    logger.error("Failed to load profile %s: %s", name, why)
                    profile = None
                self.profiles[name] = profile
            return profile

    def reload(self):
        """
        Reset profile cache and release all modules
        """
        with self.lock:
            logger.info("Reloading profiles")
            for s in self.profiles:
                logger.debug("Reload profile %s", s.name)
                reload(sys.modules[s.__module__])
            self.profiles = {}
            self.all_profiles = set()

    def is_valid_name(self, name):
        return ".." not in name

    def find_profiles(self):
        """
        Scan all available profiles
        """
        ns = set()
        for path in glob.glob("sa/profiles/*/*/__init__.py"):
            vendor, system = path.split(os.sep)[-3:-1]
            ns.add("%s.%s" % (vendor, system))
        with self.lock:
            self.all_profiles = ns

    def iter_profiles(self):
        """
        Returns all available profile names
        """
        if not self.all_profiles:
            self.find_profiles()
        for s in sorted(self.all_profiles):
            yield s

    def has_profile(self, name):
        """
        Check profile is exists
        """
        if not self.all_profiles:
            self.find_profiles()
        return name in self.all_profiles

# Create singleton object
loader = ProfileLoader()
