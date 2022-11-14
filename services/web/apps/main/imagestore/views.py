# ---------------------------------------------------------------------
# Image Store
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Third-party modules
from django.http import HttpResponse

# NOC modules
from noc.lib.app.extdocapplication import ExtDocApplication, view
from noc.main.models.imagestore import ImageStore
from noc.core.translation import ugettext as _
from noc.core.mime import _R_CONTENT_TYPE


class ImageStoreApplication(ExtDocApplication):
    title = _("Images")
    model = ImageStore
    menu = [_("Setup"), _("Images")]
    query_fields = ["name__icontains"]

    def field_content_type(self, o: ImageStore):
        return o.get_content_type()

    def field_filename(self, o: ImageStore):
        return o.file.filename if o.file else None

    def set_file(self, files, o: ImageStore, file_attrs=None):
        if "file" not in files:
            raise ValueError("File is not set")
        file_attrs = file_attrs or {}
        file = files["file"]
        if file.content_type not in _R_CONTENT_TYPE:
            raise ValueError("Unknown ContentType")
        ct = _R_CONTENT_TYPE[file.content_type]
        o.content_type = ct.value
        o.file.put(file.read(), content_type=file.content_type, filename=file_attrs.get("filename"))
        return True

    @view("^(?P<id>[0-9a-f]{24})/image/$", access="read", api=True)
    def api_image(self, request, id):
        o = self.get_object_or_404(ImageStore, id=id)
        return HttpResponse(o.file.read(), content_type=o.get_content_type())
