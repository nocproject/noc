# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Rebuild Tag Cloud
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

from pymongo import UpdateOne, DeleteOne
from pymongo.errors import BulkWriteError
# NOC modules
from noc.main.models.tag import Tag
from noc.sa.models.managedobject import ManagedObject
from noc.inv.models.networksegment import NetworkSegment


def fix():
    bulk = []
    # Model
    ex_tags = []
    print("Update models....")
    for m in [ManagedObject]:
        tags = set()
        for s in m.objects.filter(is_managed=True).exclude(tags=None).values_list('tags', flat=True).distinct():
            tags.update(s)
        for t in tags:
            bulk += [UpdateOne({
                "tag": t}, {
                "$addToSet": {
                    "models": repr(m)
                }, "$inc": {
                    "count": m.objects.filter(tags__in=["{%s}" % t]).count()
                }
            }, upsert=True)]
        ex_tags += [t.decode("utf8") for t in tags]
    # Documents
    print("Fixing documents....")
    for m in [NetworkSegment]:
        tags = set(t[0] for t in m.objects.filter(tags__exists=True).values_list('tags') if t)
        ex_tags += list(tags)
        for t in tags:
            bulk += [UpdateOne({
                "tag": t}, {
                "$addToSet": {
                    "models": repr(m)
                }, "$inc": {
                    "count": m.objects.filter(tags__in=[t]).count()
                }
            }, upsert=True)]
    delete_tags = set(Tag.objects.values_list("tag")) - set(ex_tags)
    print("Clean tags: %s" % delete_tags)
    for t in delete_tags:
        bulk += [DeleteOne({"tag": t})]
    if bulk:
        print("Commiting changes to database")
        try:
            r = Tag._get_collection().bulk_write(bulk)
            print("Database has been synced")
            print("Inserted: %d, Modify: %d, Deleted: %d" % (
                  r.inserted_count + r.upserted_count,
                  r.modified_count, r.deleted_count))
        except BulkWriteError as e:
            print("Bulk write error: '%s'", e.details)
            print("Stopping check")
