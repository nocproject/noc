# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Validation engine
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
from collections import defaultdict
import datetime
import uuid
import re
import threading
## Third-party modules
import clips
from pymongo.errors import BulkWriteError
## NOC modules
from noc.cm.facts.error import Error
from noc.cm.facts.role import Role
from noc.lib.log import PrefixLoggerAdapter
from noc.cm.models.validationpolicysettings import ValidationPolicySettings
from noc.inv.models.interface import Interface as InvInterface
from noc.inv.models.subinterface import SubInterface as InvSubInterface
from noc.lib.debug import error_report
from noc.lib.solutions import get_solution
from noc.cm.models.objectfact import ObjectFact
from noc.lib.clipsenv import CLIPSEnv

logger = logging.getLogger(__name__)


class Engine(object):
    ILOCK = threading.Lock()
    AC_POLICY_VIOLATION = None

    def __init__(self, object):
        self.object = object
        self.logger = PrefixLoggerAdapter(logger, self.object.name)
        self.env = None
        self.templates = {}  # fact class -> template
        self.fcls = {}  # template -> Fact class
        self.facts = {}  # Index -> Fact
        self.rn = 0  # Rule number
        self.config = None  # Cached config
        self.interface_ranges = None
        with self.ILOCK:
            self.AC_POLICY_VIOLATION = AlarmClass.objects.filter(
                name="Config | Policy Violation").first()
            if not self.AC_POLICY_VIOLATION:
                logger.error("Alarm class 'Config | Policy Violation' is not found. Alarms cannot be raised")

    def get_template(self, fact):
        if fact.cls not in self.templates:
            self.logger.debug("Creating template %s", fact.cls)
            self.templates[fact.cls] = self.env.BuildTemplate(
                fact.cls, fact.get_template())
            self.fcls[fact.cls] = fact.__class__
            self.logger.debug("Define template %s",
                              self.templates[fact.cls].PPForm())
        return self.templates[fact.cls]

    def get_rule_number(self):
        return self.rn

    def assert_fact(self, fact):
        f = self.get_template(fact).BuildFact()
        f.AssignSlotDefaults()
        for k, v in fact.iter_factitems():
            if v is None or v == [] or v == tuple():
                continue
            if isinstance(v, basestring):
                v = v.replace("\n", "\\n")
            f.Slots[k] = v
        try:
            f.Assert()
        except clips.ClipsError, why:
            self.logger.error("Could not assert: %s", f.PPForm())
            self.logger.error(
                "CLIPS Error: %s\n%s",
                why,
                clips.ErrorStream.Read()
            )
            return
        self.facts[f.Index] = fact
        self.logger.debug("Assert %s", f.PPForm())

    def learn(self, gen):
        """
        Learn sequence of facts
        """
        n = 0
        for f in gen:
            if hasattr(f, "managed_object") and f.managed_object is not None:
                f.bind()
                # @todo: Custom bindings from solutions
            self.assert_fact(f)
            n += 1

    def iter_errors(self):
        """
        Generator yielding known errors
        """
        try:
            e = self.templates["error"].InitialFact()
        except TypeError:
            raise StopIteration
        while e:
            if e.Slots.has_key("obj"):
                obj = e.Slots["obj"]
                if hasattr(obj, "Index"):
                    # obj is a fact
                    if obj.Index in self.facts:
                        obj = self.facts[obj.Index]
            else:
                obj = None
            error = Error(e.Slots["type"], obj=obj, msg=e.Slots["msg"])
            if e.Index not in self.facts:
                self.facts[e.Index] = error
            yield error
            e = e.Next()

    def iter_roles(self):
        """
        Generator yielding role fact
        """
        try:
            e = self.templates["role"].InitialFact()
        except TypeError:
            raise StopIteration
        while e:
            role = Error(e.Slots["name"])
            if e.Index not in self.facts:
                self.facts[e.Index] = role
            yield role
            e = e.Next()

    def run(self):
        """
        Run engine round
        :returns: Number of matched rules
        """
        return self.env.Run()

    def add_rule(self, expr):
        self.env.Build(expr)
        self.rn += 1

    def check(self):
        with CLIPSEnv() as env:
            self.setup_env(env)
            self._check()

    def _check(self):
        """
        Perform object configuration check
        """
        self.logger.info("Checking %s", self.object)
        parser = self.object.get_parser()
        self.config = self.object.config.read()
        if not self.config:
            self.logger.error("No config for %s. Giving up", self.object)
            return
        # Parse facts
        self.logger.debug("Parsing facts")
        facts = list(parser.parse(self.config))
        self.logger.debug("%d facts are extracted", len(facts))
        self.interface_ranges = parser.interface_ranges
        self.logger.debug("%d interface sections detected",
                          len(self.interface_ranges))
        # Define default templates
        self.get_template(Error(None))
        self.get_template(Role(None))
        # Learn facts
        self.logger.debug("Learning facts")
        self.learn(facts)
        self.logger.debug("Learning complete")
        # Install rules
        rules = []
        for r in self.get_rules():
            if r.is_applicable():
                self.logger.debug("Using validation rule: %s",
                                  r.rule.name)
                try:
                    cfg = r.get_config()
                    r.prepare(**cfg)
                except clips.ClipsError, why:
                    self.logger.error(
                        "CLIPS Error: %s\n%s",
                        why,
                        clips.ErrorStream.Read()
                    )
                    continue
                except:
                    error_report()
                    continue
                rules += [(r, cfg)]
        # Run python validators
        for r, cfg in rules:
            r.check(**cfg)
        # Run CLIPS engine
        while True:
            self.logger.debug("Running engine")
            n = self.run()
            self.logger.debug("%d rules matched", n)
            break  # @todo: Check for commands
        # Extract errors
        for e in self.iter_errors():
            self.logger.info("Error found: %s", e)
        # Store object's facts
        self.sync_facts()
        # Manage related alarms
        if self.AC_POLICY_VIOLATION:
            self.sync_alarms()

    def _get_rule_settings(self, ps, scope):
        """
        Process PolicySettings object and returns a list of
        (validator class, config)
        """
        r = []
        for pi in ps.policies:
            policy = pi.policy
            if not pi.is_active or not policy.is_active:
                continue
            for ri in policy.rules:
                if not ri.is_active:
                    continue
                rule = ri.rule
                if rule.is_active and rule.is_applicable_for(self.object):
                    vc = get_solution(rule.handler)
                    if vc and bool(vc.SCOPE & scope):
                        r += [(vc, rule)]
        return r

    def _get_rules(self, model, id, scope, obj=None):
        ps = ValidationPolicySettings.objects.filter(
            model_id=model, object_id=str(id)
        ).first()
        if not ps or not ps.policies:
            return []
        return [
            vc(self, obj, rule.config, scope, rule)
            for vc, rule in self._get_rule_settings(ps, scope)
        ]

    def get_rules(self):
        r = []
        # Object profile rules
        if self.object.object_profile:
            r += self._get_rules(
                "sa.ManagedObjectProfile",
                self.object.object_profile.id,
                BaseValidator.OBJECT,
                self.object
            )
        # Object rules
        r += self._get_rules(
            "sa.ManagedObject",
            self.object.id,
            BaseValidator.OBJECT,
            self.object
        )
        # Interface rules
        profile_interfaces = defaultdict(list)
        for i in InvInterface.objects.filter(managed_object=self.object.id):
            if i.profile:
                profile_interfaces[i.profile] += [i]
            r += self._get_rules(
                "inv.Interface",
                i.id,
                BaseValidator.INTERFACE,
                i
            )
        # Interface profile rules
        for p in profile_interfaces:
            ps = ValidationPolicySettings.objects.filter(
                model_id="inv.InterfaceProfile", object_id=str(p.id)
            ).first()
            if not ps or not ps.policies:
                continue
            rs = self._get_rule_settings(ps, BaseValidator.INTERFACE)
            if rs:
                for iface in profile_interfaces[p]:
                    r += [
                        vc(self, iface, rule.config,
                           BaseValidator.INTERFACE, rule)
                        for vc, rule in rs
                    ]
        # Subinterface profile rules
        profile_subinterfaces = defaultdict(list)
        for si in InvSubInterface.objects.filter(managed_object=self.object.id):
            p = si.get_profile()
            if p:
                profile_subinterfaces[p] += [si]
        for p in profile_subinterfaces:
            ps = ValidationPolicySettings.objects.filter(
                model_id="inv.InterfaceProfile", object_id=str(p.id)
            ).first()
            if not ps or not ps.policies:
                continue
            rs = self._get_rule_settings(ps, BaseValidator.SUBINTERFACE)
            if rs:
                for si in profile_subinterfaces[p]:
                    r += [
                        vc(self, si, rule.config,
                           BaseValidator.SUBINTERFACE, rule)
                        for vc, rule in rs
                    ]
        return r

    def get_fact_uuid(self, fact):
        r = [str(self.object.id), fact.cls] + [str(getattr(fact, n)) for n in fact.ID]
        return uuid.uuid5(
            uuid.NAMESPACE_URL,
            "-".join(r)
        )

    def get_fact_attrs(self, fact):
        return dict(fact.iter_factitems())

    def sync_facts(self):
        """
        Retrieve known facts and synchronize with database
        """
        self.logger.debug("Synchronizing facts")
        # Get facts from CLIPS
        self.logger.debug("Extracting facts")
        e_facts = {}  # uuid -> fact
        try:
            f = self.env.InitialFact()
        except clips.ClipsError, w:
            return  # No facts
        while f:
            if f.Template and f.Template.Name in self.templates:
                self.facts[f.Index] = f
                args = {}
                for k in f.Slots.keys():
                    v = f.Slots[k]
                    if v == clips.Nil:
                        v = None
                    args[str(k)] = v
                fi = self.fcls[f.Template.Name](**args)
                e_facts[self.get_fact_uuid(fi)] = fi
            f = f.Next()
        # Get facts from database
        now = datetime.datetime.now()
        collection = ObjectFact._get_collection()
        bulk = collection.initialize_unordered_bulk_op()
        new_facts = set(e_facts)
        changed = False
        for f in collection.find({"object": self.object.id}):
            if f["_id"] in e_facts:
                fact = e_facts[f["_id"]]
                f_attrs = self.get_fact_attrs(fact)
                if f_attrs != f["attrs"]:
                    # Changed facts
                    self.logger.debug(
                        "Fact %s has been changed: %s -> %s",
                        f["_id"], f["attrs"], f_attrs)
                    bulk.find({"_id": f["_id"]}).update({
                        "$set": {
                            "attrs": f_attrs,
                            "changed": now,
                            "label": unicode(fact)
                        }
                    })
                    changed = True
                new_facts.remove(f["_id"])
            else:
                # Removed fact
                self.logger.debug("Fact %s has been removed", f["_id"])
                bulk.find({"_id": f["_id"]}).remove()
                changed = True
        # New facts
        for f in new_facts:
            fact = e_facts[f]
            f_attrs = self.get_fact_attrs(fact)
            self.logger.debug("Creating fact %s: %s", f, f_attrs)
            bulk.insert({
                "_id": f,
                "object": self.object.id,
                "cls": fact.cls,
                "label": unicode(fact),
                "attrs": f_attrs,
                "introduced": now,
                "changed": now
            })
        if new_facts:
            changed = True
        if changed:
            self.logger.debug("Commiting changes to database")
            try:
                bulk.execute()
                self.logger.debug("Database has been synced")
            except BulkWriteError, bwe:
                self.logger.error("Bulk write error: '%s'", bwe.details)
                self.logger.error("Stopping check")
        else:
            self.logger.debug("Nothing changed")

    def compile_query(self, **kwargs):
        def wrap(x):
            for k in kwargs:
                if getattr(x, k, None) != kwargs[k]:
                    return False
            return True

        return wrap

    def find(self, **kwargs):
        """
        Search facts for match. Returns a list of matching facts
        """
        q = self.compile_query(**kwargs)
        return [f for f in self.facts.itervalues() if q(f)]

    def find_one(self, **kwargs):
        """
        Search for first matching fact. Returns fact or None
        """
        q = self.compile_query(**kwargs)
        for f in self.facts.itervalues():
            if q(f):
                return f
        return None

    def sync_alarms(self):
        """
        Raise/close related alarms
        """
        # Check errors are exists
        n_errors = sum(1 for e in self.iter_errors())
        alarm = ActiveAlarm.objects.filter(
            alarm_class=self.AC_POLICY_VIOLATION.id,
            managed_object=self.object.id).first()
        if n_errors:
            if not alarm:
                self.logger.info("Raise alarm")
                # Raise alarm
                alarm = ActiveAlarm(
                    timestamp=datetime.datetime.now(),
                    managed_object=self.object,
                    alarm_class=self.AC_POLICY_VIOLATION,
                    severity=2000  # WARNING
                )
            # Alarm is already exists
            alarm.log_message("%d errors has been found" % n_errors)
        elif alarm:
            # Clear alarm
            self.logger.info("Clear alarm")
            alarm.clear_alarm("No errors has been registered")

    def setup_env(self, env):
        """
        Install additional CLIPS functions
        """
        logger.debug("Setting up CLIPS environment")
        self.env = env
        # Create wrappers
        logger.debug("Install function: match-re")
        env.BuildFunction(
            "match-re",
            "?rx ?s",
            "(return (python-call py-match-re ?rx ?s))"
        )

#
from noc.cm.validators.base import BaseValidator
from noc.fm.models.alarmclass import AlarmClass
from noc.fm.models.activealarm import ActiveAlarm
