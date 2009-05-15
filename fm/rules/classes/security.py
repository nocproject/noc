# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Security Events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from noc.fm.rules.classes import EventClass,Var

##
## ACL Reject
##
class ACLReject(EventClass):
    name     = "ACL Reject"
    category = "SECURITY"
    priority = "NORMAL"
    subject_template="Packet rejected by ACL: {{src_ip}}:{{src_port}} -> {{dst_ip}}:{{dst_port}}"
    body_template="""ACL Name: {{acl_name}}
Action: REJECT
Packets count: {{count}}
Direction: {{src_ip}}:{{src_port}} -> {{dst_ip}}:{{dst_port}}"""
    repeat_suppression=True
    repeat_suppression_interval=3600
    trigger=None
    class Vars:
        acl_name=Var(required=False,repeat=False)
        count=Var(required=False,repeat=False)
        src_port=Var(required=True,repeat=False)
        src_ip=Var(required=True,repeat=True)
        dst_ip=Var(required=True,repeat=True)
        dst_port=Var(required=True,repeat=True)
        proto=Var(required=False,repeat=False)
##
## ACL Permit
##
class ACLPermit(EventClass):
    name     = "ACL Permit"
    category = "SECURITY"
    priority = "INFO"
    subject_template="Packet permitted by ACL: {{src_ip}}:{{src_port}} -> {{dst_ip}}:{{dst_port}}"
    body_template="""ACL Name: {{acl_name}}
Action: PERMIT
Packets count: {{count}}
Direction: {{src_ip}}:{{src_port}} -> {{dst_ip}}:{{dst_port}}"""
    repeat_suppression=True
    repeat_suppression_interval=3600
    trigger=None
    class Vars:
        acl_name=Var(required=False,repeat=False)
        count=Var(required=False,repeat=False)
        src_port=Var(required=True,repeat=False)
        src_ip=Var(required=True,repeat=True)
        dst_ip=Var(required=True,repeat=True)
        dst_port=Var(required=True,repeat=True)
        proto=Var(required=False,repeat=False)
