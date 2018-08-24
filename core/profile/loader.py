# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Profile loader
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from __future__ import absolute_import
import sys
import glob
import logging
import os
import threading
# NOC modules
from noc.core.loader.base import BaseLoader
from .base import BaseProfile

GENERIC_PROFILE = "Generic.Host"


class ProfileLoader(BaseLoader):
    name = "profile"

    def __init__(self):
        super(ProfileLoader, self).__init__()
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
                self.logger.info("Loading profile %s", name)
                if not self.is_valid_name(name):
                    self.logger.error("Invalid profile name")
                    return None
                if name == GENERIC_PROFILE:
                    module_name = "noc.sa.profiles.Generic"
                else:
                    module_name = "noc.sa.profiles.%s" % name
                for mn in ("%s.profile" % module_name, module_name):
                    profile = self.find_class(mn, BaseProfile, name)
                    if profile:
                        if not profile.__module__.endswith(".profile"):
                            self.logger.info(
                                "Deprecation warning on %s profile: "
                                "__init__.py should be moved to profile.py", name)
                        profile.initialize()
                        break
                self.profiles[name] = profile
            return profile

    def reload(self):
        """
        Reset profile cache and release all modules
        """
        with self.lock:
            self.logger.info("Reloading profiles")
            for s in self.profiles:
                self.logger.debug("Reload profile %s", s.name)
                reload(sys.modules[s.__module__])
            self.profiles = {}
            self.all_profiles = set()

    def is_valid_name(self, name):
        return ".." not in name

    def find_profiles(self):
        """
        Scan all available profiles
        """
        ns = set([GENERIC_PROFILE])
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

    def choices(self):
        return [(p, p) for p in self.iter_profiles()]


# Create singleton object
loader = ProfileLoader()
