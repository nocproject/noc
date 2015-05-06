# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.inv data plugin
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from base import InvPlugin
from noc.inv.models.object import Object
from noc.sa.interfaces.base import UnicodeParameter


class CommentPlugin(InvPlugin):
    name = "comment"
    js = "NOC.inv.inv.plugins.comment.CommentPanel"

    def init_plugin(self):
        super(CommentPlugin, self).init_plugin()
        self.add_view(
            "api_plugin_%s_set_comment" % self.name,
            self.api_set_comment,
            url="^(?P<id>[0-9a-f]{24})/plugin/%s/$" % self.name,
            method=["POST"],
            validate={
                "comment": UnicodeParameter()
            }
        )

    def get_data(self, request, o):
        return {
            "id": str(o.id),
            "comment": o.comment.read() or ""
        }

    def api_set_comment(self, request, id, comment):
        o = self.app.get_object_or_404(Object, id=id)
        o.comment.write(comment.encode("utf8"))
        return True