# ---------------------------------------------------------------------
# ./noc wipe
# ---------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import argparse
import sys
from contextlib import contextmanager
from typing import List

# NOC modules
from noc.core.management.base import BaseCommand, CommandError
from noc.core.mongo.connection import connect
from noc.core.validators import is_int
from noc.core.change.policy import change_tracker
from noc.models import get_model


class Command(BaseCommand):
    args = "<model> <object id> [.. <object id>]. Model is managed_object or user"
    help = "Completely wipe object and related data"

    models = {"managed_object": "sa.ManagedObject", "user": "aaa.User"}

    def add_arguments(self, parser):
        parser.add_argument("model", nargs=1, help="List of extractor names")
        parser.add_argument("--state", help="Filter by state (if model supported")
        parser.add_argument(
            "--dry-run",
            dest="dry_run",
            action="store_true",
            help="Dump statistics. Do not perform updates",
        )
        parser.add_argument("ids", nargs=argparse.REMAINDER, help="List of extractor names")

    def handle(
        self, model, state=None, dry_run: bool = False, ids: List[str] = None, *args, **options
    ):
        """"""
        print(model, state, args, ids)
        connect()
        objects = []
        if model[0] in self.models:
            wiper = getattr(self, f"wipe_{model[0]}")
            model = self.models[model[0]]
        else:
            wiper = self.wipe_default
            model = model[0]
        for o in self.iter_objects(model, ids, state):
            objects += [o]
        if dry_run:
            self.print(f"Wiping {len(objects)} objects")
            return
        # Wipe objects
        from noc.core.debug import error_report

        with change_tracker.bulk_changes():
            for o in objects:
                with self.log(f"Wiping '{o}':", True):
                    try:
                        wiper(o)
                    except KeyboardInterrupt:
                        raise CommandError("Interrupted. Wiping is not complete")
                    except Exception:
                        error_report()

    def iter_objects(self, mid, ids: List[str], state=None):
        if state:
            self.print("Iter objects with state")
        model = get_model(mid)
        if state:
            for o in model.objects.filter(state=state):
                yield o
        if mid == "sa.ManagedObject":
            g = self.get_managed_object
        elif mid == "aaa.User":
            g = self.get_user
        else:
            g = model.get_by_id
        for o_id in ids:
            o = g(o_id)
            if not o:  # Not found
                raise CommandError("Object '%s' is not found" % o_id)
            yield o

    def handle_1(self, *args, **options):
        if len(args) < 1:
            print("USAGE: %s <model> <object id> [.. <object id>]" % sys.argv[0])
            sys.exit(1)
        m = args[0].replace("-", "_")
        connect()
        if m not in self.models:
            raise CommandError(
                "Invalid model '%s'. Valid models are: %s" % (m, ", ".join(self.models))
            )
        objects = []
        getter = getattr(self, "get_%s" % m)
        wiper = getattr(self, "wipe_%s" % m)
        # Get objects
        for o_id in args[1:]:
            o = getter(o_id)
            if not o:  # Not found
                raise CommandError("Object '%s' is not found" % o_id)
            objects += [o]
        # Wipe objects
        from noc.core.debug import error_report

        with change_tracker.bulk_changes():
            for o in objects:
                with self.log(f"Wiping '{o}':", True):
                    try:
                        wiper(o)
                    except KeyboardInterrupt:
                        raise CommandError("Interrupted. Wiping is not complete")
                    except Exception:
                        error_report()

    @contextmanager
    def log(self, message, newline=False):
        """
        Progress log wrapper. Usage:
        with self.log(message):
            do something

        :param message:
        :param newline: Add newline
        :return:
        """
        if newline:
            message += "\n"
        else:
            message = "    " + message + " ... "
        sys.stdout.write(message)
        sys.stdout.flush()
        yield
        sys.stdout.write("done\n")
        sys.stdout.flush()

    def get_managed_object(self, o_id):
        """
        Get ManagedObject by id or name
        :param o_id: Object's id or name
        :return: ManagedObject
        :rtype: ManagedObject
        """
        from noc.sa.models.managedobject import ManagedObject

        # Try to get object by id
        if is_int(o_id):
            try:
                return ManagedObject.objects.get(id=int(o_id))
            except ManagedObject.DoesNotExist:
                pass
        # Try to get object by name
        try:
            return ManagedObject.objects.get(name=o_id)
        except ManagedObject.DoesNotExist:
            return None

    def wipe_default(self, o):
        o.delete()

    def wipe_managed_object(self, o):
        """
        Wipe Managed Object
        :param o: Managed Object
        :type o: Managed Object
        :return: None
        """
        from noc.sa.wipe.managedobject import wipe

        wipe(o)

    def get_user(self, u_id):
        """
        Get User by id or name
        :param u_id: Object's id or name
        :return: ManagedObject
        :rtype: ManagedObject
        """
        from noc.aaa.models.user import User

        # Try to get object by id
        if is_int(u_id):
            try:
                return User.objects.get(id=int(u_id))
            except User.DoesNotExist:
                pass
        # Try to get object by name
        try:
            return User.objects.get(username=u_id)
        except User.DoesNotExist:
            return None

    @staticmethod
    def clean_django_log_entry(user):
        # Third-party modules
        from django.db import connection as pg_connect

        cursor = pg_connect.cursor()
        query = "DELETE FROM django_admin_log WHERE user_id = %d" % user.id
        cursor.execute(query)

    def wipe_user(self, o):
        """
        Wipe User
        :param o: User
        :type o: User
        :return: None
        """
        from noc.main.models.notificationgroup import NotificationGroupUser
        from noc.main.models.audittrail import AuditTrail
        from noc.aaa.models.usercontact import UserContact
        from noc.aaa.models.permission import Permission
        from noc.main.models.userstate import UserState
        from noc.main.models.favorites import Favorites
        from noc.sa.models.useraccess import UserAccess
        from noc.fm.models.activealarm import ActiveAlarm
        from noc.ip.models.prefixaccess import PrefixAccess
        from noc.ip.models.prefixbookmark import PrefixBookmark
        from noc.kb.models.kbentrypreviewlog import KBEntryPreviewLog
        from noc.kb.models.kbentryhistory import KBEntryHistory
        from noc.kb.models.kbuserbookmark import KBUserBookmark

        # Clean UserState
        with self.log("Cleaning user preferences"):
            UserState.objects.filter(user_id=o.id).delete()
        # Clean NotificationGroupUser
        with self.log("Cleaning audit trail"):
            AuditTrail.objects.filter(user=o.username).delete()
        # Clean NotificationGroupUser
        with self.log("Cleaning notification groups"):
            NotificationGroupUser.objects.filter(user=o).delete()
        # Clean User contact
        with self.log("Cleaning user contact"):
            UserContact.objects.filter(user=o).delete()
        # Clean user access
        with self.log("Cleaning management object access"):
            UserAccess.objects.filter(user=o).delete()
        # Clean user permission
        with self.log("Cleaning permission access"):
            Permission.objects.filter(users=o).delete()
        # Unsubscribe from alarms
        with self.log("Unsubscribing from alarms"):
            for a in ActiveAlarm.objects.filter(subscribers=o.id):
                a.subscribers = [s for s in a.subscribers if s != o]
                a.save()
        # Revoke prefix access
        with self.log("Revoking prefix access"):
            PrefixAccess.objects.filter(user=o).delete()
        # Clean Prefix Bookmarks
        with self.log("Cleaning prefix bookmarks"):
            PrefixBookmark.objects.filter(user=o).delete()
        # Clean Favorites Bookmarks
        with self.log("Cleaning favorites bookmarks"):
            Favorites.objects.filter(user=o).delete()
        # Clean KB Preview log
        with self.log("Cleaning KB preview log"):
            KBEntryPreviewLog.objects.filter(user=o).delete()
        # Clean KB User Bookmarks
        with self.log("Cleaning KB user bookmarks"):
            KBUserBookmark.objects.filter(user=o).delete()
        # Clean KB Entry History
        with self.log("Cleaning KB user history"):
            KBEntryHistory.objects.filter(user=o).delete()

        # Finally delete user
        with self.log("Deleting user"):
            o.delete()


if __name__ == "__main__":
    Command().run()
