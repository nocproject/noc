# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Small DSL for event classification rules description
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import re
from noc.fm.rules.classes.default import Default
from noc.fm.models import MIB,EventClass,EventClassificationRule,EventClassificationRE,MIBNotFoundException

re_var=re.compile(r"\(\?P<([^>]+>)\)")
##
##
##
event_class_cache={}
def get_event_class(ec):
    global event_class_cache
    if ec not in event_class_cache:
        event_class_cache[ec.name]=EventClass.objects.get(name=ec.name)
    return event_class_cache[ec.name]

##
## ClassigicationRule metaclass
## Performs regexp patterns checking
##
class ClassificationRuleBase(type):
    def __new__(cls,name,bases,attrs):
        m=type.__new__(cls,name,bases,attrs)
        vars={}
        # Check regular expressions in patters
        for p in m.patterns:
            if p.__class__==Expression:
                pass
            else:
                l,r=p
                try:
                    re.compile(l)
                    re.compile(r,re.MULTILINE|re.DOTALL)
                except:
                    raise Exception("Invalid pattern ('%s','%s') in rule %s"%(l,r,m.name))
        # Check variables
        return m
##
## Rule actions
##
MAKE_ACTIVE="A"
DROP_EVENT="D"
CLOSE_EVENT="C"
##
## Event classification rule
##
class ClassificationRule(object):
    __metaclass__=ClassificationRuleBase
    name="Classification Rule"
    event_class=Default
    preference=1000
    action=MAKE_ACTIVE
    required_mibs=[] # A list of required MIB Names
    patterns=[]  # Pair of (left_re,right_re)
    ##
    ## Syncronize class with database
    ##
    @classmethod
    def sync(cls):
        # Check all required MIBs are uploaded
        for mib_name in cls.required_mibs:
            try:
                mib=MIB.objects.get(name=mib_name)
            except MIB.DoesNotExist:
                raise MIBNotFoundException(mib_name)
        # Create or update event classification rule
        try:
            r=EventClassificationRule.objects.get(name=cls.name)
            r.event_class=get_event_class(cls.event_class)
            r.preference=cls.preference
            r.action=cls.action
            r.is_builtin=True
            print "UPDATE RULE %s"%cls.name
        except EventClassificationRule.DoesNotExist:
            r=EventClassificationRule(
                event_class=get_event_class(cls.event_class),
                name=cls.name,
                preference=cls.preference,
                action=cls.action,
                is_builtin=True
            )
            print "CREATE RULE %s"%cls.name
        r.save()
        r.eventclassificationre_set.all().delete()
        for p in cls.patterns:
            if p.__class__==Expression:
                EventClassificationRE(rule=r,left_re=p.left,right_re=p.right,is_expression=True).save()
            else:
                rx_l,rx_r=p
                EventClassificationRE(rule=r,left_re=rx_l,right_re=rx_r).save()
##
## Wrapper for expression variables
##
class Expression(object):
    def __init__(self,left,right):
        self.left=left
        compile(right,"inline","eval") # Raise SyntaxError in case of invalid expression
        self.right=right
