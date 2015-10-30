# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Rule
##----------------------------------------------------------------------
## Copyright (C) 2007-2012, The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.main.models import PyRule
from noc.lib.datasource import datasource_registry


class Rule(object):
    def __init__(self, ec, dr):
        self.name = dr.name
        self.event_class = ec
        self.u_name = "%s: %s" % (self.event_class.name, self.name)
        self.condition = compile(dr.condition, "<string>", "eval")
        mo_exp = dr.managed_object or "event.managed_object"
        self.managed_object = compile(mo_exp, "<string>", "eval")
        try:
            self.conditional_pyrule = PyRule.objects.get(
                name=ec.conditional_pyrule_name,
                interface="IDispositionCondition")
        except PyRule.DoesNotExist:
            self.conditional_pyrule = None
        self.action = dr.action
        self.alarm_class = dr.alarm_class
        self.stop_disposition = dr.stop_disposition
        self.var_mapping = {}
        self.discriminator = []
        self.datasources = {}
        self.c_defaults = {}
        self.d_defaults = {}
        if self.alarm_class:
            self.severity = self.alarm_class.default_severity.severity
            self.unique = self.alarm_class.is_unique
            a_vars = set([v.name for v in self.alarm_class.vars])
            e_vars = set([v.name for v in self.event_class.vars])
            for v in a_vars.intersection(e_vars):
                self.var_mapping[v] = v
            if dr.var_mapping:
                self.var_mapping.update(dr.var_mapping)
            self.discriminator = self.alarm_class.discriminator
            self.combo_condition = dr.combo_condition
            self.combo_window = dr.combo_window
            self.combo_event_classes = [c.id for c in dr.combo_event_classes]
            self.combo_count = dr.combo_count
            # Default variables
            for v in self.alarm_class.vars:
                if v.default:
                    if v.default.startswith("="):
                        # Expression
                        self.d_defaults[v.name] = compile(
                            v.default[1:], "<string>", "eval")
                    else:
                        # Constant
                        self.c_defaults[v.name] = v.default
            # Compile datasource lookup functions
            self.datasources = {}  # name -> ds class
            for ds in self.alarm_class.datasources:
                self.datasources[ds.name] = eval(
                    "lambda vars: datasource_registry['%s'](%s)" % (
                        ds.datasource,
                        ", ".join(["%s=vars['%s']" % (k, v)
                                   for k, v in ds.search.items()])),
                    {"datasource_registry": datasource_registry}, {})

    def get_vars(self, e):
        """
        Get alarm variables from event.

        :param e: ActiveEvent
        :returns: tuple of (discriminator, vars)
        """
        if self.var_mapping:
            vars = self.c_defaults.copy()
            # Map vars
            for k, v in self.var_mapping.items():
                try:
                    vars[v] = e.vars[k]
                except KeyError:
                    pass
            # Calculate dynamic defaults
            ds_vars = vars.copy()
            ds_vars["managed_object"] = e.managed_object
            context = dict((k, v(ds_vars))
                for k, v in self.datasources.items())
            context.update(vars)
            for k, v in self.d_defaults.items():
                x = eval(v, {}, context)
                if x:
                    vars[k] = x
            # Calculate discriminator
            discriminator = self.alarm_class.get_discriminator(vars)
            return discriminator, vars
        else:
            return self.alarm_class.get_discriminator({}), None
