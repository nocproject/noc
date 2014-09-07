# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## RepoInline
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------


class RepoInline(object):
    def __init__(self, field):
        self.field = field
        self.app = None
        self.parent_model = None

    def contribute_to_class(self, app, name):
        # Get last revision
        app.add_view("api_%s_get" % name,
            self.api_get, method=["GET"],
            url="^(?P<parent>[^/]+)/repo/%s/$" % name,
            access="read", api=True)
        # Get list of revisions
        app.add_view("api_%s_revisions" % name,
            self.api_revisions, method=["GET"],
            url="^(?P<parent>[^/]+)/repo/%s/revisions/$" % name,
            access="read", api=True)
        # Get particular revision
        app.add_view("api_%s_get_revision" % name,
            self.api_get_revision, method=["GET"],
            url="^(?P<parent>[^/]+)/repo/%s/(?P<revision>[0-9a-f]{24})/$" % name,
            access="read", api=True)
        # Get diff
        app.add_view("api_%s_diff" % name,
            self.api_get_diff, method=["GET"],
            url="^(?P<parent>[^/]+)/repo/%s/(?P<rev1>[0-9a-f]{24})/(?P<rev2>[0-9a-f]{24})/$" % name,
            access="read", api=True)

    def set_app(self, app):
        self.app = app
        self.logger = app.logger
        self.parent_model = self.app.model

    def get_field(self, parent):
        o = self.app.get_object_or_404(self.parent_model, id=int(parent))
        return getattr(o, self.field)

    def api_get(self, request, parent):
        return self.get_field(parent).read()

    def api_revisions(self, request, parent):
        f = self.get_field(parent)
        return [{
            "id": str(r.id),
            "ts": r.ts.isoformat()
        } for r in f.get_revisions(reverse=True)]

    def api_get_revision(self, request, parent, revision):
        return self.get_field(parent).get_revision(revision)

    def api_get_diff(self, request, parent, rev1, rev2):
        return self.get_field(parent).diff(rev1, rev2)
