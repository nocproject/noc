# ----------------------------------------------------------------------
# copy objects
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import os

# Third-party modules
from django.db import models

# NOC modules
from noc.core.migration.base import BaseMigration


class Migration(BaseMigration):
    depends_on = [("cm", "0009_access_and_notify"), ("cm", "0010_trap_source_ip")]

    def migrate(self):
        def qget(map, key):
            if key is None:
                return None
            return map[key]

        # Fill administrative domains
        location2domain = {}
        for id, name, description in self.db.execute(
            "SELECT id,name,description FROM cm_objectlocation"
        ):
            self.db.execute(
                "INSERT INTO sa_administrativedomain(name,description) VALUES(%s,%s)",
                [name, description],
            )
            location2domain[id] = self.db.execute(
                "SELECT id FROM sa_administrativedomain WHERE name=%s", [name]
            )[0][0]
        # Fill groups
        category2group = {}
        for id, name, description in self.db.execute(
            "SELECT id,name,description FROM cm_objectcategory"
        ):
            self.db.execute(
                "INSERT INTO sa_objectgroup(name,description) VALUES(%s,%s)", [name, description]
            )
            category2group[id] = self.db.execute(
                "SELECT id FROM sa_objectgroup WHERE name=%s", [name]
            )[0][0]
        ManagedObject = self.db.mock_model(model_name="ManagedObject", db_table="sa_managedobject")
        self.db.add_column(
            "cm_config",
            "managed_object",
            models.ForeignKey(ManagedObject, null=True, on_delete=models.CASCADE),
        )

        # Move objects
        for (
            id,
            repo_path,
            activator_id,
            profile_name,
            scheme,
            address,
            port,
            user,
            password,
            super_password,
            remote_path,
            location_id,
            trap_source_ip,
            trap_community,
        ) in self.db.execute(
            """
                SELECT id,repo_path,activator_id,profile_name,scheme,address,port,\"user\",password,super_password,
                remote_path,location_id,trap_source_ip,trap_community FROM cm_config"""
        ):
            name = os.path.basename(repo_path)
            self.db.execute(
                """INSERT INTO sa_managedobject(name,repo_path,activator_id,profile_name,scheme,address,port,\"user\",
                    password,super_password,remote_path,administrative_domain_id,trap_source_ip,trap_community)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                [
                    name,
                    repo_path,
                    activator_id,
                    profile_name,
                    scheme,
                    address,
                    port,
                    user,
                    password,
                    super_password,
                    remote_path,
                    location2domain[location_id],
                    trap_source_ip,
                    trap_community,
                ],
            )
            new_id = self.db.execute("SELECT id FROM sa_managedobject WHERE name=%s", [name])[0][0]
            for object_id, objectcategory_id in self.db.execute(
                "SELECT object_id,objectcategory_id FROM cm_object_categories WHERE object_id=%s",
                [id],
            ):
                self.db.execute(
                    "INSERT INTO sa_managedobject_groups(manageobject_id,objectgroup_id) VALUES(%s,%s)",
                    [new_id, category2group[objectcategory_id]],
                )
            self.db.execute("UPDATE cm_config SET managed_object_id=%s WHERE id=%s", [new_id, id])
        # Move user access
        for category_id, location_id, user_id in self.db.execute(
            "SELECT category_id,location_id,user_id FROM cm_objectaccess"
        ):
            self.db.execute(
                "INSERT INTO sa_useraccess(user_id,administrative_domain_id,group_id) VALUES(%s,%s,%s)",
                [user_id, qget(location2domain, location_id), qget(category2group, category_id)],
            )
        self.db.execute("ALTER TABLE cm_config ALTER managed_object_id SET NOT NULL")

        # Migrate ObjectNotify
        ObjectGroup = self.db.mock_model(model_name="ObjectGroup", db_table="sa_objectgroup")
        AdministrativeDomain = self.db.mock_model(
            model_name="AdministrativeDomain", db_table="sa_administrativedomain"
        )

        self.db.add_column(
            "cm_objectnotify",
            "administrative_domain",
            models.ForeignKey(
                AdministrativeDomain,
                verbose_name="Administrative Domain",
                blank=True,
                null=True,
                on_delete=models.CASCADE,
            ),
        )
        self.db.add_column(
            "cm_objectnotify",
            "group",
            models.ForeignKey(
                ObjectGroup, verbose_name="Group", blank=True, null=True, on_delete=models.CASCADE
            ),
        )
        for id, category_id, location_id in self.db.execute(
            "SELECT id,category_id,location_id FROM cm_objectnotify"
        ):
            self.db.execute(
                "UPDATE cm_objectnotify SET administrative_domain_id=%s,group_id=%s WHERE id=%s",
                [qget(location2domain, location_id), qget(category2group, category_id), id],
            )
