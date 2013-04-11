# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## main.update application
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.lib.app import ExtApplication, view
from noc.main.models.manifest import Manifest
from noc.lib.serialize import json_decode
from noc.lib.fileutils import read_file


class UpdateApplication(ExtApplication):
    """
    main.update application
    """
    title = "Update"

    @view(url="^$", access=True, api=True, method=["POST"])
    def api_update(self, request):
        manifest = {}
        for name in request.GET.getlist("name"):
            manifest.update(Manifest.get_manifest(name))
        r = []
        for path, hash in json_decode(request.raw_post_data):
            if path in manifest:
                if manifest[path] != hash:
                    # File changed
                    r += [[path, hash, read_file(path)]]
            else:
                # Remove file
                r += [[path, None, None]]
        return r
