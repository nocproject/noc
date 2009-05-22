# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Small DSL for event correlation rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.fm.models import EventCorrelationRule,EventCorrelationMatchedClass,EventCorrelationMatchedVar,EventClass

CLOSE_EVENT="C"
##
event_class_cache={}
def get_event_class(ec):
    global event_class_cache
    if ec not in event_class_cache:
        event_class_cache[ec.name]=EventClass.objects.get(name=ec.name)
    return event_class_cache[ec.name]
##
## Basic event correlation rule
##
class CorrelationRule(object):
    name="Corellation Rule" # Name of the rule
    description=""          # Description
    rule_type="Pair"        # Matching algorithm
    action=CLOSE_EVENT      # Action
    same_object=True        # Restrict search to the same managed object
    window=0                # Time window
    classes=[]              # Classes to match
    vars=[]                 # variables to match
    
    @classmethod
    def sync(cls):
        try:
            r=EventCorrelationRule.objects.get(name=cls.name)
            r.description=cls.description
            r.rule_type=cls.rule_type
            r.action=cls.action
            r.same_object=cls.same_object
            r.window=cls.window
            r.is_builtin=True
            print "UPDATE CORRELATION RULE %s"%cls.name
        except EventCorrelationRule.DoesNotExist:
            r=EventCorrelationRule(
                name=cls.name,
                description=cls.description,
                rule_type=cls.rule_type,
                action=cls.action,
                same_object=cls.same_object,
                window=cls.window,
                is_builtin=True
            )
            print "CREATE CORRELATION RULE %s"%cls.name
        r.save()
        r.eventcorrelationmatchedclass_set.all().delete()
        for c in cls.classes:
            EventCorrelationMatchedClass(rule=r,event_class=get_event_class(c)).save()
        r.eventcorrelationmatchedvar_set.all().delete()
        for v in cls.vars:
            EventCorrelationMatchedVar(rule=r,var=v).save()
