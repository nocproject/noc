# ---------------------------------------------------------------------
# inv.inv data plugin
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.http import HttpRequest

# NOC modules
from noc.inv.models.object import Object
from noc.sa.interfaces.base import UnicodeParameter
from .base import InvPlugin


class CommentPlugin(InvPlugin):
    name = "comment"
    js = "NOC.inv.inv.plugins.comment.CommentPanel"

    def init_plugin(self):
        super().init_plugin()
        self.add_view(
            f"api_plugin_{self.name}_set_comment",
            self.api_set_comment,
            url=f"^(?P<id>[0-9a-f]{{24}})/plugin/{self.name}/$",
            method=["POST"],
            validate={"comment": UnicodeParameter()},
        )

    def get_data(self, request: HttpRequest, o):
        return {"id": str(o.id), "comment": o.comment.read() or ""}

    def api_set_comment(self, request: HttpRequest, id, comment):
        o = self.app.get_object_or_404(Object, id=id)
        o.comment.write(comment.encode("utf8"))
        return True
