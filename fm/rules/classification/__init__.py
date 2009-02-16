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
        for l,r in m.patterns:
            try:
                re.compile(l)
                re.compile(r,re.MULTILINE|re.DOTALL)
            except:
                raise Exception("Invalid pattern ('%s','%s') in rule %s"%(l,r,m.name))
        # Check variables
        return m
##
## Event classification rule
##
class ClassificationRule(object):
    __metaclass__=ClassificationRuleBase
    name="Classification Rule"
    event_class=Default
    preference=1000
    drop_event=False
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
            r.drop_event=cls.drop_event
            r.is_builtin=True
            print "UPDATE RULE %s"%cls.name
        except EventClassificationRule.DoesNotExist:
            r=EventClassificationRule(
                event_class=get_event_class(cls.event_class),
                name=cls.name,
                preference=cls.preference,
                drop_event=cls.drop_event,
                is_builtin=True
            )
            print "CREATE RULE %s"%cls.name
        r.save()
        [rx.delete() for rx in r.eventclassificationre_set.all()]
        for rx_l,rx_r in cls.patterns:
            rx=EventClassificationRE(rule=r,left_re=rx_l,right_re=rx_r)
            rx.save()
