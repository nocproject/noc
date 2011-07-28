# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Report Application
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import Application, PermitLogged, view


class ReportAppplication(Application):
    """
    Report application
    """
    title = "Reports"

    @view(url=r"^$", url_name="index", menu="Reports", access=PermitLogged())
    def view_index(self,request):
        """
        Render report index
        """
        # Find available reports
        modules = []  # {title,reports}
        for r in [r for r in self.site.reports
                  if r.view_report.access.check(r, request.user)]:
            if not modules or modules[-1]["title"] != r.module_title:
                modules += [{"title": r.module_title, "reports": [r]}]
            else:
                modules[-1]["reports"] += [r]
        # Sort reports
        for m in modules:
            reports = sorted(m["reports"], lambda x, y: cmp(x.title, y.title))
            m["reports"] = [{
                "title"  : r.title,
                "html"   : self.site.reverse(r.app_id.replace(".",":") + ":view", "html"),
                "formats": [(f,self.site.reverse(r.app_id.replace(".",":") + ":view", f))
                            for f in r.supported_formats() if f != "html"]
                } for r in reports]
        return self.render(request, "index.html", modules=modules)
