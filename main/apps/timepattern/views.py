# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.timepattern application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
from noc.lib.app import ExtModelApplication, view
from noc.main.models.timepattern import TimePattern
from noc.main.models.timepatternterm import TimePatternTerm
from noc.lib.app.modelinline import ModelInline
from noc.sa.interfaces.base import ModelParameter, ListOfParameter, StringParameter


class TimePatternApplication(ExtModelApplication):
    """
    TimePattern application
    """
    title = "Time Pattern"
    menu = "Setup | Time Patterns"
    model = TimePattern
    glyph = "clock-o"

    terms = ModelInline(TimePatternTerm)

    @view(url="^actions/test/", method=["POST"],
          access="read", api=True,
          validate={
              "ids": ListOfParameter(element=ModelParameter(TimePattern)),
              "date": StringParameter(required=True),
              "time": StringParameter(required=True),
          })
    def api_action_test(self, request, ids, date=None, time=None):
        d = "%sT%s" % (date, time)
        dt = datetime.datetime.strptime(d, "%Y-%m-%dT%H:%M")
        return {
            "ts": dt.isoformat(),
            "result": [{
                "id": p.id,
                "name": p.name,
                "result": p.match(dt)
            } for p in ids]
        }


