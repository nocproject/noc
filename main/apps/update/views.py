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

    @view(url="^$", access=True, api=True, method=["GET"])
    def api_update(self, request):
        if not hasattr(self, "repo"):
            self.repo = localrepo.localrepository(ui.ui(), path=".")
            self.tip = "".join("%02x" % ord(c) for c in self.repo.changelog.tip())
            self.branch = self.repo.dirstate.branch()

        return [
            {
                "name": "noc",
                "repo": "http://%s/hg/noc/" % request.META["HTTP_HOST"],
                "branch": self.branch,
                "tip": self.tip
            }
        ]
