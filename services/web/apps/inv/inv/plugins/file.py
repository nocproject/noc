# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## inv.inv file plugin
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import datetime
## NOC modules
from base import InvPlugin
from noc.inv.models.object import Object
from noc.inv.models.objectfile import ObjectFile
from noc.main.models import MIMEType


class FilePlugin(InvPlugin):
    name = "file"
    js = "NOC.inv.inv.plugins.file.FilePanel"

    def init_plugin(self):
        super(FilePlugin, self).init_plugin()
        self.add_view(
            "api_plugin_%s_upload" % self.name,
            self.api_upload,
            url="^(?P<id>[0-9a-f]{24})/plugin/%s/upload/$" % self.name,
            method=["POST"]
        )
        self.add_view(
            "api_plugin_%s_download" % self.name,
            self.api_download,
            url="^(?P<id>[0-9a-f]{24})/plugin/%s/(?P<file_id>[0-9a-f]{24})/$" % self.name,
            method=["GET"]
        )
        self.add_view(
            "api_plugin_%s_delete" % self.name,
            self.api_delete,
            url="^(?P<id>[0-9a-f]{24})/plugin/%s/(?P<file_id>[0-9a-f]{24})/$" % self.name,
            method=["DELETE"]
        )

    def get_data(self, request, o):
        files = []
        for f in ObjectFile.objects.filter(object=o.id).order_by("name"):
            files += [{
                "id": str(f.id),
                "name": f.name,
                "mime_type": f.mime_type,
                "size": f.size,
                "ts": f.ts.isoformat(),
                "description": f.description
            }]
        return {
            "id": str(o.id),
            "files": files
        }

    def api_upload(self, request, id):
        o = self.app.get_object_or_404(Object, id=id)
        left = {}  # name -> data
        for f in request.FILES:
            left[f] = request.FILES[f]
        errors = {}
        failed = False
        for name in left:
            # file_XXX -> description_XXX
            dn = "description_%s" % name[5:]
            f = left[name]
            of = ObjectFile(
                object=o.id,
                name=f.name,
                size=f.size,
                mime_type=MIMEType.get_mime_type(f.name),
                ts=datetime.datetime.now(),
                description=request.POST.get(dn)
            )
            of.file.put(f.read())
            of.save()
        return {
            "success": not failed,
            "errors": errors
        }

    def api_download(self, request, id, file_id):
        o = self.app.get_object_or_404(Object, id=id)
        of = self.app.get_object_or_404(ObjectFile, id=file_id)
        if of.object != o.id:
            return self.app.response_not_found()
        return self.app.render_response(
            of.file.read(),
            content_type=of.mime_type
        )

    def api_delete(self, request, id, file_id):
        o = self.app.get_object_or_404(Object, id=id)
        of = self.app.get_object_or_404(ObjectFile, id=file_id)
        if of.object != o.id:
            return self.app.response_not_found()
        of.delete()
        return True
