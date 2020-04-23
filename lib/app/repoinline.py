# ---------------------------------------------------------------------
# RepoInline
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party libraries
from django.http import Http404


class RepoInline(object):
    def __init__(self, field, access="read"):
        self.field = field
        self.app = None
        self.parent_model = None
        self.access = access
        self.check_access = None
        self.logger = None

    def contribute_to_class(self, app, name):
        # Get last revision
        app.add_view(
            "api_%s_get" % name,
            self.api_get,
            method=["GET"],
            url="^(?P<parent>[^/]+)/repo/%s/$" % name,
            access=self.access,
            api=True,
        )
        # Get list of revisions
        app.add_view(
            "api_%s_revisions" % name,
            self.api_revisions,
            method=["GET"],
            url="^(?P<parent>[^/]+)/repo/%s/revisions/$" % name,
            access=self.access,
            api=True,
        )
        # Get particular revision
        app.add_view(
            "api_%s_get_revision" % name,
            self.api_get_revision,
            method=["GET"],
            url="^(?P<parent>[^/]+)/repo/%s/(?P<revision>[0-9a-f]{24})/$" % name,
            access=self.access,
            api=True,
        )
        # Get diff
        app.add_view(
            "api_%s_diff" % name,
            self.api_get_diff,
            method=["GET"],
            url="^(?P<parent>[^/]+)/repo/%s/(?P<rev1>[0-9a-f]{24})/(?P<rev2>[0-9a-f]{24})/$" % name,
            access=self.access,
            api=True,
        )
        # Get mdiff
        app.add_view(
            "api_%s_mdiff" % name,
            self.api_get_mdiff,
            method=["GET"],
            url="^(?P<parent>[^/]+)/repo/%s/(?P<rev1>[0-9a-f]{24})/(?P<obj2>[^/]+)/(?P<rev2>[0-9a-f]{24})/$"
            % name,
            access=self.access,
            api=True,
        )

    def set_app(self, app):
        self.app = app
        self.logger = app.logger
        self.parent_model = self.app.model
        self.check_access = getattr(self.app, "has_repo_%s_access" % self.field, None)

    def clean_parent(self, v):
        return int(v)

    def get_parent(self, user, parent):
        o = self.app.get_object_or_404(self.parent_model, id=self.clean_parent(parent))
        if self.check_access and not self.check_access(user, o):
            raise Http404("Not found")
        return o

    def get_field(self, user, parent):
        return getattr(self.get_parent(user, parent), self.field)

    def api_get(self, request, parent):
        return self.get_field(request.user, parent).read()

    def api_revisions(self, request, parent):
        f = self.get_field(request.user, parent)
        return [{"id": str(r.id), "ts": r.ts.isoformat()} for r in f.get_revisions(reverse=True)]

    def api_get_revision(self, request, parent, revision):
        return self.get_field(request.user, parent).get_revision(revision)

    def api_get_diff(self, request, parent, rev1, rev2):
        c = self.get_field(request.user, parent).diff(rev1, rev2)
        return c if c else "IS EQUAL"

    def api_get_mdiff(self, request, parent, rev1, obj2, rev2):
        c = self.get_field(request.user, parent).mdiff(rev1, self.clean_parent(obj2), rev2)
        return c if c else "IS EQUAL"
