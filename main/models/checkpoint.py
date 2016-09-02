# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Database triggers
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models
from noc.core.translation import ugettext as _
from django.contrib.auth.models import User


class Checkpoint(models.Model):
    """
    Checkpoint is a marked moment in time
    """

    class Meta:
        verbose_name = _("Checkpoint")
        verbose_name_plural = _("Checkpoints")

    timestamp = models.DateTimeField(_("Timestamp"))
    user = models.ForeignKey(User, verbose_name=_("User"), blank=True, null=True)
    comment = models.CharField(_("Comment"), max_length=256)
    private = models.BooleanField(_("Private"), default=False)

    def __unicode__(self):
        if self.user:
            return u"%s[%s]: %s" % (self.timestamp, self.user.username,
                                    self.comment)

    @classmethod
    def set_checkpoint(cls, comment, user=None, timestamp=None, private=True):
        if not timestamp:
            timestamp = datetime.datetime.now()
        cp = Checkpoint(timestamp=timestamp, user=user, comment=comment,
                        private=private)
        cp.save()
        return cp
