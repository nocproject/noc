# -*- coding: utf-8 -*-
from south.db import db
<<<<<<< HEAD
=======
from noc.main.models import *
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


class Migration:
    depends_on = (
        ("main", "0018_systemnotification"),
        )

    def forwards(self):
        if not db.execute(
            "SELECT COUNT(*) FROM main_systemnotification WHERE name=%s"
            , ["dns.domain_expired"])[0][0]:
            db.execute(
                "INSERT INTO main_systemnotification(name) VALUES(%s)",
                ["dns.domain_expired"])
        if not db.execute(
            "SELECT COUNT(*) FROM main_systemnotification WHERE name=%s"
            , ["dns.domain_expiration_warning"])[0][0]:
            db.execute(
                "INSERT INTO main_systemnotification(name) VALUES(%s)",
                ["dns.domain_expiration_warning"])

    def backwards(self):
        """Write your backwards migration here"""
