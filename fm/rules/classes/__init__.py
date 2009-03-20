# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Small DSL for event class description
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.models import EventCategory,EventPriority,EventClassVar,event_trigger_registry
import noc.fm.models
import re

rx_var=re.compile("{{([^}]+)}}")
##
## EventCategory cache
##
category_cache={}
def get_category(name):
    global category_cache
    if name not in category_cache:
        try:
            category_cache[name]=EventCategory.objects.get(name=name)
        except EventCategory.DoesNotExist:
            category_cache[name]=EventCategory(name=name)
            category_cache[name].save()
    return category_cache[name]
##
## EventPriority cache
##
priority_cache={}
def get_priority(name):
    global priority_cache
    if name not in priority_cache:
        priority_cache[name]=EventPriority.objects.get(name=name)
    return priority_cache[name]
    
##
## Event class variable placeholder.
## Used inside class Vars of Event Class
##
class Var(object):
    def __init__(self,required=True,repeat=False):
        self.required=required
        self.repeat=repeat
##
## Metaclass performing registration
## and variable checking
##
class EventClassBase(type):
    def __new__(cls,name,bases,attrs):
        def get_vars(s):
            vars=rx_var.findall(s)
            if vars:
                return dict(zip(vars,vars))
            else:
                return {}
        m=type.__new__(cls,name,bases,attrs)
        #
        # Extract vars from Vars class
        #
        m.vars={}
        for vn in [v for v in dir(m.Vars)]:
            v=getattr(m.Vars,vn)
            if isinstance(v,Var):
                m.vars[vn]=v
        #
        # Check templates contain no undefined variables
        #
        tv={}
        tv.update(get_vars(m.subject_template))
        tv.update(get_vars(m.body_template))
        for v in tv:
            if v not in m.vars:
                raise Exception("Unknown variable '%s' in template"%v)
        #
        return m
##
## Base class for event class descriptions
##
class EventClass(object):
    __metaclass__=EventClassBase
    name="Event Class"
    category="DEFAULT"
    priority="DEFAULT"
    subject_template=""
    body_template=""
    repeat_suppression=False
    repeat_suppression_interval=3600
    trigger=None
    class Vars: pass
    ##
    ## Syncronize class with database
    ##
    @classmethod
    def sync(cls):
        # Check trigger
        if cls.trigger and cls.trigger not in event_trigger_registry.classes:
            raise "Invalid event trigger: %s"%cls.trigger
        # Create/update event class
        try:
            ec=noc.fm.models.EventClass.objects.get(name=cls.name)
            ec.category=get_category(cls.category)
            ec.default_priority=get_priority(cls.priority)
            ec.subject_template=cls.subject_template
            ec.body_template=cls.body_template
            ec.repeat_suppression=cls.repeat_suppression
            ec.repeat_suppression_interval=cls.repeat_suppression_interval
            ec.trigger=cls.trigger
            ec.is_builtin=True
            print "UPDATE CLASS %s"%cls.name
        except noc.fm.models.EventClass.DoesNotExist:
            ec=noc.fm.models.EventClass(
                name=cls.name,
                category=get_category(cls.category),
                default_priority=get_priority(cls.priority),
                subject_template=cls.subject_template,
                body_template=cls.body_template,
                repeat_suppression=cls.repeat_suppression,
                repeat_suppression_interval=cls.repeat_suppression_interval,
                trigger=cls.trigger,
                is_builtin=True)
            print "CREATE CLASS %s"%cls.name
        ec.save()
        # Syncronize vars
        ec.eventclassvar_set.all().delete()
        for name,var in cls.vars.items():
            v=EventClassVar(event_class=ec,name=name,required=var.required,repeat_suppression=var.repeat)
            v.save()
