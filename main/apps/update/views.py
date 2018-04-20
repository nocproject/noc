# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.update application
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from mercurial import ui, localrepo
## NOC modules
from noc.lib.app import ExtApplication, view


class UpdateApplication(ExtApplication):
    """
    main.update application
    """
    title = "Update"

    def get_url(self, request):
        proto = "https" if request.is_secure() else "http"
        return "%s://%s/" % (proto, request.META["HTTP_HOST"])

    @view(url="^$", access=True, api=True, method=["GET"])
    def api_update(self, request):
        if not hasattr(self, "repo"):
            self.repo = localrepo.localrepository(ui.ui(), path=".")
            self.tip = "".join("%02x" % ord(c) for c in self.repo.changelog.tip())
            self.branch = self.repo.dirstate.branch()

        return [
            {
                "name": "noc",
                "repo": "%shg/noc/" % self.get_url(request),
                "branch": self.branch,
                "tip": self.tip
            }
        ]

    @view(url="^make-node\.py$", access=True, api=True, method=["GET"])
    def api_make_node(self, request):
        with open("scripts/make-node.py") as f:
            data = f.read()
        data = data.replace("URL = \"\"",
                            "URL = \"%s\"" % self.get_url(request))
        return self.render_plain_text(data)
