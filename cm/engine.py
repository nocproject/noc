# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Validation engine
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import logging
## Third-party modules
import clips
from noc.cm.facts.error import Error

logger = logging.getLogger(__name__)


class Engine(object):
    def __init__(self):
        logger.debug("Creating CLIPS environment")
        self.env = clips.Environment()
        self.templates = {}  # fact class -> template
        self.get_template(Error(None))
        self.facts = {}  # Index -> Fact

    def get_template(self, fact):
        if fact.cls not in self.templates:
            logger.debug("Creating template %s", fact.cls)
            self.templates[fact.cls] = self.env.BuildTemplate(
                fact.cls, fact.get_template())
        return self.templates[fact.cls]

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
            logger.debug("Assert [%s].%s = %s", unicode(fact), k, v)
            f.Slots[k] = v
        f.Assert()
        fact._index = f.Index
        self.facts[f.Index] = fact

    def learn(self, gen):
        """
        Learn sequence of facts
        """
        n = 0
        for f in gen:
            self.assert_fact(f)
            n += 1
        logger.debug("%d facts learned", n)

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
                self.facts[e.Index] = Error
            yield error
            e = e.Next()

    def run(self):
        """
        Run engine round
        :returns: Number of matched rules
        """
        return self.env.Run()
