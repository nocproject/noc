# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Configuration Management Object
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import os
import datetime
## Django modules
from django.db import models
from django.db.models import Q
## NOC modules
from noc.settings import config
from noc.lib.fileutils import rewrite_when_differ, read_file, is_differ, in_dir
from noc.cm.vcs import vcs_registry
from noc.lib.validators import is_int
from objectnotify import ObjectNotify
from noc.main.models.notificationgroup import NotificationGroup


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


## Avoid circular references
from prefixlist import PrefixList
from rpsl import RPSL