# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ./noc wipe
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
from __future__ import with_statement
import sys
from contextlib import contextmanager
## Django modules
from django.core.management.base import BaseCommand, CommandError
## NOC modules
from noc.lib.validators import is_int


class Command(BaseCommand):
    args = "<model> <object id> [.. <object id>]"
    help = "Completely wipe object and related data"

    models = ["managed_object", "user"]

    def handle(self, *args, **options):
        if len(args) < 1:
            print "USAGE: %s <model> <object id> [.. <object id>]" % sys.argv[0]
            sys.exit(1)
        m = args[0].replace("-", "_")
        if m not in self.models:
            raise CommandError("Invalid model '%s'. Valid models are: %s" % (
                m, ", ".join(self.models)))
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
        from noc.lib.debug import error_report
        for o in objects:
            with self.log("Wiping '%s':" % unicode(o), True):
                try:
                    wiper(o)
                except KeyboardInterrupt:
                    raise CommandError("Interrupted. Wiping is not complete")
                except:
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
            :param o_id: Object's id or name
            :return: ManagedObject
            :rtype: ManagedObject
            """
            from django.contrib.auth.models import User

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

    def wipe_user(self, o):
        """
        Wipe User
        :param o: User
        :type o: User
        :return: None
        """
        from noc.main.models import AuditTrail, NotificationGroupUser,\
                                    UserProfile, Checkpoint, UserState
        from noc.sa.models.useraccess import UserAccess
        from noc.fm.models.activealarm import ActiveAlarm
        from noc.ip.models.prefixaccess import PrefixAccess
        from noc.ip.models.prefixbookmark import PrefixBookmark
        from noc.kb.models import KBEntryPreviewLog, KBUserBookmark
        # Clean UserState
        with self.log("Cleaning user preferences"):
            UserState.objects.filter(user_id=o.id).delete()
        # Clean NotificationGroupUser
        with self.log("Cleaning audit trail"):
            AuditTrail.objects.filter(user=o.username).delete()
        # Clean NotificationGroupUser
        with self.log("Cleaning notification groups"):
            NotificationGroupUser.objects.filter(user=o).delete()
        # Clean User profile
        with self.log("Cleaning user profile"):
            UserProfile.objects.filter(user=o).delete()
        # Clean Checkpoint
        with self.log("Cleaning checkpoints"):
            Checkpoint.objects.filter(user=o).delete()
        # Clean user access
        with self.log("Cleaning management object access"):
            UserAccess.objects.filter(user=o).delete()
        # Reset owned alarms
        with self.log("Revoking assigned alarms"):
            for a in ActiveAlarm.objects.filter(owner=o.id):
                a.owner = None
                a.save()
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
        # Clean KB Preview log
        with self.log("Cleaning KB preview log"):
            KBEntryPreviewLog.objects.filter(user=o).delete()
        # Clean KB User Bookmarks
        with self.log("Cleaning KB user bookmarks"):
            KBUserBookmark.objects.filter(user=o).delete()
        # Finally delete user
        with self.log("Deleting user"):
            o.delete()
