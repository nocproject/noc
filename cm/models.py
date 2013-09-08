# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Configuration Management models
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import datetime
import logging
import types
import difflib
## Django modules
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
## NOC modules
from noc.sa.profiles import profile_registry
from noc.settings import config
from noc.lib.fileutils import rewrite_when_differ, read_file, is_differ, in_dir
from noc.lib.validators import is_int
from noc.cm.vcs import vcs_registry
from noc.sa.models import AdministrativeDomain, ManagedObject
from noc.lib.search import SearchResult
from noc.main.models import NotificationGroup
from noc.lib.app.site import site


profile_registry.register_all()
vcs_registry.register_all()

#
OBJECT_TYPES = ["config", "dns", "prefix-list", "rpsl"]
OBJECT_TYPE_CHOICES = [(x, x) for x in OBJECT_TYPES if x != "config"]


class ObjectNotify(models.Model):
    class Meta:
        verbose_name = "Object Notify"
        verbose_name_plural = "Object Notifies"

    type = models.CharField("Type", max_length=16, choices=OBJECT_TYPE_CHOICES)
    administrative_domain = models.ForeignKey(AdministrativeDomain,
                                              verbose_name="Administrative Domain",
                                              blank=True, null=True)
    notify_immediately = models.BooleanField("Notify Immediately")
    notify_delayed = models.BooleanField("Notify Delayed")
    notification_group = models.ForeignKey(NotificationGroup,
                                           verbose_name="Notification Group")

    def __unicode__(self):
        return u"(%s, %s, %s)" % (self.type, self.administrative_domain,
                                  self.notification_group)

    def get_absolute_url(self):
        return site.reverse("cm:objectnotify:change", self.id)


class Object(models.Model):
    class Meta:
        abstract = True

    repo_path = models.CharField("Repo Path", max_length=128, unique=True)
    #
    last_modified = models.DateTimeField("Last Modified", blank=True, null=True)
    #
    push_every = models.PositiveIntegerField("Push Every (secs)", default=86400,
                                             blank=True, null=True)
    next_push = models.DateTimeField("Next Push", blank=True, null=True)
    last_push = models.DateTimeField("Last Push", blank=True, null=True)
    #
    pull_every = models.PositiveIntegerField("Pull Every (secs)", default=86400,
                                             blank=True, null=True)
    next_pull = models.DateTimeField("Next Pull", blank=True, null=True)
    last_pull = models.DateTimeField("Last Pull", blank=True,
                                     null=True)  # Updated by write() method

    def __unicode__(self):
        return u"%s/%s" % (self.repo_name, self.repo_path)

    @property
    def vcs(self):
        return vcs_registry.get(self.repo)

    def save(self, *args, **kwargs):
        if self.repo_path and not in_dir(self.path, self.repo):
            raise Exception("Attempting to write outside of repo")
        mv = None
        if self._get_pk_val():
            old = self.__class__.objects.get(pk=self._get_pk_val())
            if old.repo_path != self.repo_path and old.repo_path != ".":
                mv = (old.repo_path, self.repo_path)
        models.Model.save(self, *args, **kwargs)
        vcs = self.vcs
        if mv is not None and vcs.in_repo(mv[0]):
            vcs.mv(mv[0], mv[1])

    @property
    def repo(self):
        return os.path.join(config.get("cm", "repo"), self.repo_name)

    @property
    def path(self):
        return os.path.join(self.repo, self.repo_path)

    @property
    def in_repo(self):
        """
        Check object is in repository
        :return: True if object is present, False otherwise
        """
        return self.vcs.in_repo(self.repo_path)

    def status(self):
        return {True: "Ready", False: "Waiting"}[self.in_repo]

    def write(self, data):
        """
        Write data to repository and commit
        :param data:
        :return:
        """
        path = self.path
        if not in_dir(path, self.repo):
            raise Exception("Attempting to write outside of repo")
        is_new = not os.path.exists(path)
        now = datetime.datetime.now()
        if rewrite_when_differ(self.path, data):
            vcs = self.vcs
            if is_new:
                vcs.add(self.repo_path)
            vcs.commit(self.repo_path)
            self.last_modified = now
            self.on_object_changed()
        self.last_pull = now
        self.save()

    @property
    def data(self):
        """
        Return object's content or None, if not present
        :return: Object content
        """
        return read_file(self.path)

    def delete(self):
        if os.path.exists(self.repo_path):
            self.vcs.rm(self.path)
        super(Object, self).delete()

    @property
    def revisions(self):
        """
        Get list of revisions
        :return:
        """
        return self.vcs.log(self.repo_path)

    # Finds revision of the object and returns Revision
    def find_revision(self, rev):
        assert is_int(rev)
        for r in self.revisions:
            if r.revision == rev:
                return r
        raise Exception("Not found")

    # Return object's current revision
    @property
    def current_revision(self):
        """
        Get object's current revision
        :return:
        """
        return self.vcs.get_current_revision(self.repo_path)

    def diff(self, rev1, rev2):
        return self.vcs.diff(self.repo_path, rev1, rev2)

    def get_revision(self, rev):
        return self.vcs.get_revision(self.repo_path, rev)

    def annotate(self):
        return self.vcs.annotate(self.repo_path)

    @classmethod
    def get_object_class(self, repo):
        if repo == "prefix-list":
            return PrefixList
        elif repo == "rpsl":
            return RPSL
        else:
            raise Exception("Invalid repo '%s'" % repo)

    @property
    def module_name(self):
        """
        object._meta.model_name
        :return:
        """
        return self._meta.module_name

    @property
    def verbose_name_plural(self):
        """
        Shortcut to object._meta.verbose_name_plural
        """
        return self._meta.verbose_name_plural

    @property
    def verbose_name(self):
        return self._meta.verbose_name

    def get_notification_groups(self, immediately=False, delayed=False):
        q = Q(type=self.repo_name)
        if immediately:
            q &= Q(notify_immediately=True)
        if delayed:
            q &= Q(notify_delayed=True)
        return set(
            [n.notification_group for n in ObjectNotify.objects.filter(q)])

    def notification_diff(self, old_data, new_data):
        return self.diff(old_data, new_data)

    def on_object_changed(self):
        notification_groups = self.get_notification_groups(immediately=True)
        if not notification_groups:
            return
        revs = self.revisions
        now = datetime.datetime.now()
        if len(revs) == 1:
            # @todo: replace with template
            subject = "NOC: Object '%s' was created" % str(self)
            message = "The object %s was created at %s\n" % (str(self), now)
            message += "Object value follows:\n---------------------------\n%s\n-----------------------\n" % self.data
            link = None
        else:
            diff = self.notification_diff(revs[1], revs[0])
            if not diff:
                # No significant difference to notify
                return
            subject = "NOC: Object changed '%s'" % str(self)
            message = "The object %s was changed at %s\n" % (str(self), now)
            message += "Object changes follows:\n---------------------------\n%s\n-----------------------\n" % diff
            link = None
        NotificationGroup.group_notify(groups=notification_groups,
                                       subject=subject, body=message,
                                       link=link)

    def push(self):
        pass

    def pull(self):
        pass

    @classmethod
    def global_push(self):
        """
        Push all objects of the given type
        :return:
        """
        pass

    @classmethod
    def global_pull(self):
        """
        Pull all objects of the given type
        :return:
        """
        pass

    def has_access(self, user):
        """
        Chech user has permission to access an object
        :param user:
        :return:
        """
        if user.is_superuser:
            return True
        return False

    @classmethod
    def search(cls, user, query, limit):
        """
        Search engine plugin
        :param cls:
        :param user:
        :param query:
        :param limit:
        :return:
        """
        for o in [o for o in cls.objects.all() if
                  o.repo_path and o.has_access(user)]:
            try:
                data = o.data
                if query in o.repo_path:  # If repo_path matches
                    yield SearchResult(
                        url=("cm:%s:view" % o.repo_name, o.id),
                        title="CM: " + unicode(o),
                        text=unicode(o),
                        relevancy=1.0,  # No weighted search yes
                    )
                elif data and query in data:  # Dumb substring search in config
                    idx = data.index(query)
                    idx_s = max(0, idx - 100)
                    idx_e = min(len(data), idx + len(query) + 100)
                    text = data[idx_s:idx_e]
                    yield SearchResult(
                        url=("cm:%s:view" % o.repo_name, o.id),
                        title="CM: " + unicode(o),
                        text=text,
                        relevancy=1.0,  # No weighted search yes
                    )
            except UnicodeDecodeError:  # Skip unicode errors in configs
                pass


class PrefixList(Object):
    class Meta:
        verbose_name = "Prefix List"
        verbose_name_plural = "Prefix Lists"

    repo_name = "prefix-list"

    @classmethod
    def build_prefix_lists(cls):
        from noc.peer.models import PeeringPoint, WhoisCache

        for pp in PeeringPoint.objects.all():
            profile = pp.profile
            for name, filter_exp in pp.generated_prefix_lists:
                prefixes = WhoisCache.resolve_as_set_prefixes_maxlen(filter_exp)
                pl = profile.generate_prefix_list(name, prefixes)
                yield (pp, name, pl, prefixes)

    @classmethod
    def global_pull(cls):
        from noc.peer.models import PrefixListCache, PrefixListCachePrefix

        objects = {}
        for o in PrefixList.objects.all():
            objects[o.repo_path] = o
        c_objects = set()  # peering_point/name
        logging.debug("PrefixList.global_pull(): building prefix lists")
        for peering_point, pl_name, pl, prefixes in cls.build_prefix_lists():
            logging.debug(
                "PrefixList.global_pull(): writing %s/%s (%d lines)" % (
                peering_point.hostname, pl_name, len(pl.split("\n"))))
            path = os.path.join(peering_point.hostname, pl_name)
            if path in objects:
                o = objects[path]
                del objects[path]
            else:
                o = PrefixList(repo_path=path)
                o.save()
            o.write(pl)
            # Populate cache
            cname = "%s/%s" % (peering_point.hostname, pl_name)
            try:
                c = PrefixListCache.objects.get(peering_point=peering_point.id,
                                                name=pl_name)
                if c.cmp_prefixes(prefixes):
                    logging.debug("Updating cache for %s" % cname)
                    c.changed = datetime.datetime.now()
                    c.prefixes = [PrefixListCachePrefix(prefix=prefix,
                                                        min=min, max=max)
                                  for prefix, min, max in prefixes]
                    c.save()
            except PrefixListCache.DoesNotExist:
                logging.debug("Writing cache for %s" % cname)
                PrefixListCache(peering_point=peering_point.id,
                                name=pl_name,
                                prefixes=[PrefixListCachePrefix(prefix=prefix,
                                                                min=min,
                                                                max=max)
                                          for prefix, min, max in
                                          prefixes]).save()
            c_objects.add("%s/%s" % (peering_point.hostname, pl_name))
        # Remove deleted prefix lists
        for o in objects.values():
            o.delete()
        # Remove unused cache entries
        for o in PrefixListCache.objects.all():
            n = "%s/%s" % (o.peering_point.hostname, o.name)
            if n not in c_objects:
                o.delete()


class RPSL(Object):
    class Meta:
        verbose_name = "RPSL Object"
        verbose_name_plural = "RPSL Objects"

    repo_name = "rpsl"

    @classmethod
    def global_pull(cls):
        def global_pull_class(name, c, name_fun):
            objects = {}
            for o in RPSL.objects.filter(repo_path__startswith=name + os.sep):
                objects[o.repo_path] = o
            for a in c.objects.all():
                if not a.rpsl:
                    continue
                path = os.path.join(name, name_fun(a))
                if path in objects:
                    o = objects[path]
                    del objects[path]
                else:
                    o = RPSL(repo_path=path)
                    o.save()
                o.write(a.rpsl)
            for o in objects.values():
                o.delete()

        from noc.peer.models import AS, ASSet, PeeringPoint
        from noc.dns.models import DNSZone

        logging.debug("RPSL.global_pull(): building RPSL")
        global_pull_class("inet-rtr", PeeringPoint, lambda a: a.hostname)
        global_pull_class("as", AS, lambda a: "AS%d" % a.asn)
        global_pull_class("as-set", ASSet, lambda a: a.name)
        global_pull_class("domain", DNSZone, lambda a: a.name)

    @classmethod
    def global_push(cls):
        pass
