# ---------------------------------------------------------------------
# main.timepattern application
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import datetime

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.services.web.base.extmodelapplication import ExtModelApplication, api
from noc.main.models.timepattern import TimePattern
from noc.main.models.timepatternterm import TimePatternTerm
from noc.services.web.base.modelinline import ModelInline
from noc.sa.interfaces.base import ModelParameter, ListOfParameter, StringParameter
from noc.core.translation import ugettext as _


class TimePatternApplication(ExtModelApplication):
    """
    TimePattern application
    """

    title = _("Time Pattern")
    menu = [_("Setup"), _("Time Patterns")]
    model = TimePattern
    glyph = "clock-o"

    terms = ModelInline(TimePatternTerm)

    @api.post(
        "^actions/test/",
        access="read",
        validate={
            "ids": ListOfParameter(element=ModelParameter(TimePattern)),
            "date": StringParameter(required=True),
            "time": StringParameter(required=True),
        },
    )
    def api_action_test(self, request: HttpRequest, ids, date=None, time=None):
        d = f"{date}T{time}"
        dt = datetime.datetime.strptime(d, "%Y-%m-%dT%H:%M")
        return {
            "ts": dt.isoformat(),
            "result": [{"id": p.id, "name": p.name, "result": p.match(dt)} for p in ids],
        }
