# ----------------------------------------------------------------------
# access profile
# ----------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
from urllib.parse import urlparse, unquote

# Third-party modules
from django.db import models

# NOC modules
from noc.core.script.scheme import TELNET, SSH
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    def migrate(self) -> None:
        self.db.add_column(
            "cm_object",
            "scheme",
            models.IntegerField(
                "Scheme", blank=True, null=True, choices=[(0, "telnet"), (1, "ssh")]
            ),
        )
        self.db.add_column(
            "cm_object",
            "address",
            models.CharField("Address", max_length=64, blank=True, null=True),
        )
        self.db.add_column(
            "cm_object", "port", models.PositiveIntegerField("Port", blank=True, null=True)
        )
        self.db.add_column(
            "cm_object", "user", models.CharField("User", max_length=32, blank=True, null=True)
        )
        self.db.add_column(
            "cm_object",
            "password",
            models.CharField("Password", max_length=32, blank=True, null=True),
        )
        self.db.add_column(
            "cm_object",
            "super_password",
            models.CharField("Super Password", max_length=32, blank=True, null=True),
        )
        self.db.add_column(
            "cm_object",
            "remote_path",
            models.CharField("Path", max_length=32, blank=True, null=True),
        )
        for id, url in self.db.execute(
            "SELECT id,stream_url FROM cm_object WHERE stream_url!='ssh://u:p@localhost/'"
        ):
            u = urlparse(url)
            scheme_map = {"telnet": TELNET, "ssh": SSH}
            scheme = scheme_map[u.scheme]
            host_port = u.hostname or u.netloc.split("@")[-1].split(":")[0]
            port = u.port
            user = unquote(u.username) if u.username else None
            password = unquote(u.password) if u.password else None
            remote_path = u.path if u.path and u.path != "/" else None
            self.db.execute(
                "UPDATE cm_object "
                'SET scheme=%s,address=%s,port=%s,"user"=%s,password=%s,remote_path=%s '
                "WHERE id=%s",
                [scheme, host_port, port, user, password, remote_path, id],
            )
        self.db.delete_column("cm_object", "stream_url")
