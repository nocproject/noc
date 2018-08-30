# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Create initial technologies for migration purposes
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from uuid import UUID
# Third-party modules
import bson
from bson.int64 import Int64
from pymongo import UpdateOne
# NOC modules
from noc.lib.nosql import get_db


class Migration(object):
    def forwards(self):
        bulk = [
            UpdateOne({
                "_id": bson.ObjectId("5b6d6819d706360001a0b716"),
            }, {
                "$set": {
                    "name": "Group",
                    "uuid": UUID("8874518c-effd-41fe-81bf-d67f1519ccf2"),
                    "description": "Grouping element",
                    "single_service": False,
                    "single_client": False,
                    "allow_children": True,
                    "bi_id": Int64(3859384814270643576)
                }
            }, upsert=True),
            UpdateOne({
                "_id": bson.ObjectId("5b6d6c9fd706360001f5c053"),
            }, {
                "$set": {
                    "name": "Network | Controller",
                    "uuid": UUID("bcf7ad57-81a4-4da0-8e6d-e429c9e21532"),
                    "description": "Controller - CPE relation",
                    "service_model": "sa.ManagedObject",
                    "client_model": "sa.ManagedObject",
                    "single_service": False,
                    "single_client": True,
                    "allow_children": False,
                    "bi_id": Int64(2204453448135692504)
                }
            }, upsert=True),
            UpdateOne({
                "_id": bson.ObjectId("5b6dbbefd70636000170b980")
            }, {
                "$set": {
                    "name": "Object Group",
                    "uuid": UUID("f4c6d51d-d597-4183-918e-23efd748fd12"),
                    "description": "Arbitrary group of Managed Objects",
                    "service_model": "sa.ManagedObject",
                    "single_service": False,
                    "single_client": False,
                    "allow_children": False,
                    "bi_id": Int64(4062440225872880146)
                }
            }, upsert=True),
            UpdateOne({
                "_id": bson.ObjectId("5b6d6be1d706360001f5c04e")
            }, {
                "$set": {
                    "name": "Network | IPoE Termination",
                    "uuid": UUID("ef42d9fe-d217-4754-b628-a1f71f6159da"),
                    "description": "IPoE Temination (access equipment -> BRAS)",
                    "service_model": "sa.ManagedObject",
                    "client_model": "sa.ManagedObject",
                    "single_service": False,
                    "single_client": False,
                    "allow_children": False,
                    "bi_id": Int64(4546441601898809637)
                }
            }, upsert=True),
            UpdateOne({
                "_id": bson.ObjectId("5b6d6beed706360001f5c04f")
            }, {
                "$set": {
                    "name": "Network | PPPoE Termination",
                    "uuid": UUID("a8ddcd67-d8c4-471d-9a9b-9f4749e09011"),
                    "description": "PPPoE Temination (access equipment -> BRAS)",
                    "service_model": "sa.ManagedObject",
                    "client_model": "sa.ManagedObject",
                    "single_service": False,
                    "single_client": False,
                    "allow_children": False,
                    "bi_id": Int64(3384545658468911814)
                }
            }, upsert=True),
            UpdateOne({
                "_id": bson.ObjectId("5b6d6c56d706360001f5c052")
            }, {
                "$set": {
                    "name": "Network | PPTP Termination",
                    "uuid": UUID("8ce08fc8-a5b1-448d-9c2c-ac1419ad9816"),
                    "description": "PPTP Temination (access equipment -> BRAS)",
                    "service_model": "sa.ManagedObject",
                    "client_model": "sa.ManagedObject",
                    "single_service": False,
                    "single_client": False,
                    "allow_children": False,
                    "bi_id": Int64(2085768785416150430)
                }
            }, upsert=True),
            UpdateOne({
                "_id": bson.ObjectId("5b6e785ed70636000170b9a6")
            }, {
                "$set": {
                    "name": "Voice | SIP Termination",
                    "uuid": UUID("3e15a3ea-f4c1-49a1-a183-d61dd79531c2"),
                    "description": "SIP Temination (media gateway -> softswitch)",
                    "service_model": "sa.ManagedObject",
                    "client_model": "sa.ManagedObject",
                    "single_service": False,
                    "single_client": False,
                    "allow_children": False,
                    "bi_id": Int64(4632306658633376591)
                }
            }, upsert=True)
        ]
        get_db().technologies.bulk_write(bulk)

    def backwards(self):
        pass
