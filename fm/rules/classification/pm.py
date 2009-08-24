# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Performance Management classification rules
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.fm.rules.classification import ClassificationRule,CLOSE_EVENT,DROP_EVENT
from noc.fm.rules.classes.pm import *
##
## PM OK
##
class PM_OK_Rule(ClassificationRule):
    name="PM OK"
    event_class=PMOK
    preference=5000
    patterns=[
        (r"^source$",r"^system$"),
        (r"^type$",r"^pm probe$"),
        (r"^result$",r"^0$"),
    ]
##
## PM OK
##
class PM_WARN_Rule(ClassificationRule):
    name="PM WARN"
    event_class=PMWARN
    preference=5000
    patterns=[
        (r"^source$",r"^system$"),
        (r"^type$",r"^pm probe$"),
        (r"^result$",r"^1$"),
    ]
##
## PM OK
##
class PM_FAIL_Rule(ClassificationRule):
    name="PM FAIL"
    event_class=PMFAIL
    preference=5000
    patterns=[
        (r"^source$",r"^system$"),
        (r"^type$",r"^pm probe$"),
        (r"^result$",r"^2$"),
    ]
