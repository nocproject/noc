# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Update index for selected model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Third-party modules
from whoosh.index import open_dir
## NOC modules
from noc.lib.scheduler.autointervaljob import AutoIntervalJob
from noc.main.models.fts_queue import FTSQueue
from noc.main.models import fts_models


class UpdateIndexJob(AutoIntervalJob):
    name = "main.update_index"
    threaded = True
    interval = 60
    INDEX = "local/index"

    def handler(self, *args, **kwargs):
        objects = list(FTSQueue.objects.all())
        if not objects:
            return True
        index = open_dir(self.INDEX)
        writer = index.writer()
        for q in FTSQueue.objects.all():
            if q.op == "D":
                # Delete
                self.debug("Deleting %s" % q.object)
                writer.delete_by_term("id", q.object)
            elif q.op == "U":
                # Update
                self.process_update(writer, q.object)
            q.delete()
        writer.commit()
        return True

    def process_update(self, writer, oid):
        o = self.get_object(oid)
        if not o:
            return
        i = o.get_index()
        if not i.get("content") or not i.get("id") or not i.get("url"):
            return
        self.debug(u"Updating %s %s" % (str(o._meta), unicode(o)))
        fields = {
            "id": unicode(i["id"]),
            "title": unicode(i["title"]),
            "url": unicode(),
            "content": unicode(i["content"]),
            "card": unicode(i["card"]),
        }
        if i.get("tags"):
            fields["tags"] = u",".join(i["tags"])
        writer.update_document(**fields)

    def get_object(self, oid):
        m, object_id = oid.split(":")
        if m not in fts_models:
            return None
        model = fts_models[m]
        try:
            return model.objects.get(id=int(object_id))
        except model.DoesNotExist:
            return None
