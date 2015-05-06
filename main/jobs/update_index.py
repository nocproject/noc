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


class UpdateIndexJob(AutoIntervalJob):
    name = "main.update_index"
    threaded = True
    interval = 60
    INDEX = "local/index"

    def handler(self, *args, **kwargs):
        if not FTSQueue.objects.count():
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
        o = FTSQueue.get_object(oid)
        if not o:
            return
        i = o.get_index()
        if not i.get("content") or not i.get("id"):
            return
        self.debug(u"Updating %s %s" % (str(o._meta), unicode(o)))
        fields = {
            "id": unicode(i["id"]),
            "title": unicode(i["title"]),
            "content": unicode(i["content"]),
            "card": unicode(i["card"]),
        }
        if i.get("tags"):
            fields["tags"] = u",".join(i["tags"])
        writer.update_document(**fields)
