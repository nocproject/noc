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
## Third-party modules
import clips
## NOC modules
from noc.cm.facts.error import Error
from noc.cm.facts.role import Role
from noc.lib.log import PrefixLoggerAdapter
from noc.cm.models.validationpolicysettings import ValidationPolicySettings
from noc.inv.models.interface import Interface as InvInterface
from noc.lib.debug import error_report
from noc.lib.solutions import get_solution

logger = logging.getLogger(__name__)


class Engine(object):
    def __init__(self, object):
        self.object = object
        self.logger = PrefixLoggerAdapter(logger, self.object.name)
        self.logger.debug("Creating CLIPS environment")
        self.env = clips.Environment()
        self.templates = {}  # fact class -> template
        self.get_template(Error(None))
        self.get_template(Role(None))
        self.facts = {}  # Index -> Fact
        self.rn = 0  # Rule number
        self.config = None  # Cached config

    def get_template(self, fact):
        if fact.cls not in self.templates:
            self.logger.debug("Creating template %s", fact.cls)
            self.templates[fact.cls] = self.env.BuildTemplate(
                fact.cls, fact.get_template())
            self.logger.debug("Define template %s",
                              self.templates[fact.cls].PPForm())
        return self.templates[fact.cls]

    def get_rule_number(self):
        return self.rn

    def assert_fact(self, fact):
        def _clean(v):
            if isinstance(v, (list, tuple)):
                return clips.Multifield([_clean(x) for x in v])
            elif isinstance(v, bool):
                return clips.Symbol("yes") if v else clips.Symbol("no")
            elif v is None:
                return clips.Symbol("none")
            elif isinstance(v, (int, long, float, basestring)):
                return v
            else:
                raise ValueError("Invalid data type %s" % type(v))

        f = self.get_template(fact).BuildFact()
        f.AssignSlotDefaults()
        for k, v in fact.iter_factitems():
            if v is None or v == [] or v == tuple():
                continue
            f.Slots[k] = v
        f.Assert()
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
            error = Error(e.Slots["name"], obj=obj)
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
        # Learn facts
        self.logger.debug("Learning facts")
        self.learn(facts)
        self.logger.debug("Learning complete")
        # Install rules
        rules = []
        for r in self.get_rules():
            if r.is_applicable():
                try:
                    r.prepare()
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
                rules += [r]
        # Run python validators
        for r in rules:
            cfg = r.get_config()
            r.check(**cfg)
        # Run CLIPS engine
        while True:
            self.logger.debug("Running engine")
            n = self.run()
            self.logger.debug("%d rules matched", n)
            break  # @todo: Check for commands
        # Extract errors
        for e in self.iter_errors():
            self.logger.error("Error found: %s", e)
        # @todo: Store object facts

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
                if rule.is_applicable_for(self.object):
                    vc = get_solution(rule.handler)
                    if vc and bool(vc.scope & scope):
                        r += [(vc, rule.config)]
        return r

    def _get_rules(self, model, id, scope, obj=None):
        ps = ValidationPolicySettings.objects.filter(
            model_id=model, object_id=str(id)
        ).first()
        if not ps or not ps.policies:
            return []
        return [
            vc(self, obj, config)
            for vc, config in self._get_rule_settings(ps, scope)
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
                        vc(self, iface, config)
                        for vc, config in rs
                    ]
        return r

#
from noc.cm.validators.base import BaseValidator
