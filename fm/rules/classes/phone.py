# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Telephony events
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classes import EventClass,Var
##
## Authentication Failed
##
class PhoneCall(EventClass):
    name="Phone Call"
    category="PHONE"
    priority="INFO"
    subject_template="Phone call: {{calling_number}} -> {{called_number}} (Duration: {{duration}}s, Clearing: {{call_clearing}})"
    body_template="""Phone call:
Calling number: {{calling_number}}
Called number: {{called_number}}
Duration: {{duration}}
Connect time: {{connect_time}}
Disconnect time: {{disconnect_time}}
Call clearing: {{call_clearing}}
"""
    class Vars:
        calling_number=Var(required=True)
        called_number=Var(required=True)
        connect_time=Var(required=True)
        disconnect_time=Var(required=True)
        call_clearing=Var(required=True)
        duration=Var(required=True)
