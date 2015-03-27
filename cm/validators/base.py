# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Base Validator class
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
## NOC modules
from noc.lib.solutions import solutions_roots
from noc.cm.facts.error import Error


class ValidatorRegistry(object):
    def __init__(self):
        self.validators = {}  # name -> class
        self.loaded = False

    def load_all(self):
        if self.loaded:
            return
        # Get all probes locations
        dirs = ["cm/validators"]
        for r in solutions_roots():
            d = os.path.join(r, "cm", "validators")
            if os.path.isdir(d):
                dirs += [d]
        # Load all probes
        for root in dirs:
            for path, dirnames, filenames in os.walk(root):
                for f in filenames:
                    if not f.endswith(".py") or f == "__init__.py":
                        continue
                    fp = os.path.join(path, f)
                    mn = "noc.%s" % fp[:-3].replace(os.path.sep, ".")
                    __import__(mn, {}, {}, "*")
        # Prevent further loading
        self.loaded = True

    def register(self, c):
        if not c.TITLE:
            return
        handler = "%s.%s" % (c.__module__, c.__name__)
        self.validators[handler] = c

validator_registry = ValidatorRegistry()


class ValidatorBase(type):
    def __new__(mcs, name, bases, attrs):
        m = type.__new__(mcs, name, bases, attrs)
        validator_registry.register(m)
        return m


class BaseValidator(object):
    """
    Validator base class.
    Preparation call sequence:
        validator.is_applicable()
        validator.get_priority()
        validator.prepare()

    Check call sequence:
        for v in validators:
            v.check(**v.get_config())
        engine.run()

    Then errors collected via engine.iter_errors
    """
    __metaclass__ = ValidatorBase
    TITLE = None
    DESCRIPTION = None
    PRIORITY = 1000
    CONFIG_FORM = None
    # List of tags
    TAGS = None
    # Declarative restrictions processed by default
    # is_applicable function. Items are processed sequentally
    # until first match
    # Each item is a dict of one or more fields
    #   * applicable - True (default) if validator is applicable
    #   * profile - string or re to match object's SA profile
    #   * vendor - string or re to match object's vendor
    #   * platform - string or re, or list of string or re to match platform
    #   * version - string or re, or list of string or re to match version
    restrictions = []

    INTERFACE = 1
    OBJECT = 1 << 1
    TOPOLOGY = 1 << 2
    # Validation scope
    SCOPE = OBJECT

    def __init__(self, engine, object=None, config=None, scope=None,
                 rule=None):
        """
        object depends on scope:
            * OBJECT -> Managed Object
            * INTERFACE -> Interface
        """
        self.engine = engine
        self.object = object
        self.config = config or {}
        self.scope = scope
        self.rule = rule

    def get_priority(self):
        """
        Returns rule priority. Determines check order
        """
        return self.PRIORITY

    def get_form(self):
        """
        Returns JS name of configuration form
        """
        return self.CONFIG_FORM

    def get_config(self):
        """
        Get validator config
        """
        return self.config

    def is_applicable(self):
        """
        Called to detect whether the validator is applicable
        to given managed object.
        When can_run returns True new Validator fact
        is installed to engine
        """
        def check_match(value, expr):
            if isinstance(expr, (list, tuple)):
                # List
                for x in expr:
                    if check_match(value, x):
                        return True
            elif hasattr(expr, "search"):
                # Regular expression
                return bool(expr.search(value))
            else:
                return value == expr

        def match_attr(version, rule, attr):
            v = rule.get(attr)
            if v is None:
                return True
            else:
                return check_match(getattr(version, attr), v)

        if not self.restrictions:
            return True
        v = self.object.version
        for r in self.restrictions:
            if (match_attr(v, r, "profile") and
                    match_attr(v, r, "vendor") and
                    match_attr(v, r, "platform") and
                    match_attr(v, r, "version")):
                return r.get("applicable", True)
        return False

    def prepare(self, **config):
        """
        Check preparation. Can be used to install rules
        """
        pass

    def check(self, **config):
        """
        Validate engine facts and raise error
        """
        pass

    @classmethod
    def is_interface(cls):
        return bool(cls.SCOPE & cls.INTERFACE)

    @classmethod
    def is_object(cls):
        return bool(cls.SCOPE & cls.OBJECT)

    @classmethod
    def is_topology(cls):
        return bool(cls.SCOPE & cls.TOPOLOGY)

    @property
    def object_config(self):
        return self.engine.config

    def get_interface_config(self, name):
        """
        Get interface config section
        """
        if name in self.engine.interface_ranges:
            r = []
            for start, end in self.engine.interface_ranges[name]:
                r += [self.engine.config[start:end]]
            return "".join(r)
        else:
            return ""

    def assert_error(self, name, obj=None):
        self.engine.assert_fact(Error(name, obj=obj))

#
validator_registry.load_all()