# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## pyRule model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
import threading
import datetime
## Django modules
from django.db import models
## NOC modules
from noc.sa.interfaces.base import interface_registry
from noc.lib.solutions import get_solution


class NoPyRuleException(Exception):
    pass

rx_coding = re.compile(r"^#\s*-\*-\s*coding:\s*\S+\s*-\*-\s*$", re.MULTILINE)


class PyRule(models.Model):
    class Meta:
        app_label = "main"
        db_table = "main_pyrule"
        verbose_name = "pyRule"
        verbose_name_plural = "pyRules"
        ordering = ["name"]

    name = models.CharField("Name", max_length=64, unique=True)
    interface = models.CharField("Interface", max_length=64,
            choices=[(i, i) for i in sorted(interface_registry)])
    description = models.TextField("Description")
    handler = models.CharField("Handler", max_length=255,
                               null=True, blank=True)
    text = models.TextField("Text", null=True, blank=True)
    changed = models.DateTimeField("Changed", auto_now=True, auto_now_add=True)
    # Compiled pyRules cache
    compiled_pyrules = {}
    compiled_changed = {}
    compiled_lock = threading.Lock()
    NoPyRule = NoPyRuleException

    alters_data = True   # Tell Django's template engine to not call PyRule

    # Use special filter for interface
    interface.existing_choices_filter = True

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        """
        Check syntax and save
        """
        self.compile_text(unicode(self.text))
        super(PyRule, self).save(**kwargs)

    @property
    def interface_class(self):
        """
        Get interface class
        """
        return interface_registry[self.interface]

    @classmethod
    def compile_text(self, text):
        """
        Compile pyRule
        """
        # Built-in pyRule decorator
        def pyrule(f):
            f.is_pyrule = True
            return f

        # Inject @pyrule decorator into namespace
        d = {"pyrule": pyrule}
        # Remove coding declarations and \r
        text = rx_coding.sub("", text.replace("\r\n", "\n"))
        # Compile text
        exec text in d
        # Find marked pyrule
        rules = [r for r in d.values()
                 if hasattr(r, "is_pyrule") and r.is_pyrule]
        if len(rules) < 1:
            raise SyntaxError("No @pyrule decorated symbol found")
        if len(rules) != 1:
            raise SyntaxError("More than one @pyrule deorated symbols found")
        rule = rules[0]
        if not callable(rule):
            raise SyntaxError("Rule is not callable")
        return rule

    @classmethod
    def lookup(cls, name):
        if name.startswith("noc_"):
            l = [name]
        else:
            l = [name, "noc_%s" % name]
        for n in l:
            try:
                return cls.objects.get(name=n)
            except cls.DoesNotExist:
                pass
        raise cls.NoPyRule

    def __call__(self, *args, **kwargs):
        """
        Call pyRule
        """
        if self.handler:
            f = get_solution(self.handler)
        else:
            t = datetime.datetime.now()
            # Try to get compiled rule from cache
            with self.compiled_lock:
                requires_recompile = (self.name not in self.compiled_changed or
                                      self.compiled_changed[self.name] < self.changed)
                if not requires_recompile:
                    f = self.compiled_pyrules[self.name]
            # Recompile rule and place in cache when necessary
            if requires_recompile:
                f = self.compile_text(str(self.text))
                with self.compiled_lock:
                    self.compiled_pyrules[self.name] = f
                    self.compiled_changed[self.name] = t
        # Check interface
        i = self.interface_class()
        kwargs = i.clean(**kwargs)
        # Evaluate pyRule
        result = f(*args, **kwargs)
        # Check and result
        return i.clean_result(result)

    @classmethod
    def call(cls, py_rule_name, **kwargs):
        """
        Call pyRule by name
        """
        return cls.lookup(py_rule_name)(**kwargs)
