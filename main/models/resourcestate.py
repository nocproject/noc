# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ResourceState model
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db import models


class ResourceState(models.Model):
    class Meta:
        verbose_name = "Resource State"
        verbose_name_plural = "Resource States"
        ordering = ["name"]
        app_label = "main"
        db_table = "main_resourcestate"

    name = models.CharField("Name", max_length=32, unique=True)
    description = models.TextField(null=True, blank=True)
    # State is available for selection
    is_active = models.BooleanField(default=True)
    # Only one state may be marked as "default"
    is_default = models.BooleanField(default=False)
    # State can be assigned to new record
    is_starting = models.BooleanField(default=False)
    # Resource is allowed to be provisioned
    is_provisioned = models.BooleanField(default=True)
    # Automatically step to next state when
    # resource's allocated_till field expired
    step_to = models.ForeignKey("self", blank=True, null=True)

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Reset default when necessary
        """
        if self.is_default:
            # Reset previous default
            try:
                r = ResourceState.objects.get(is_default=True)
                if r.id != self.id:
                    r.is_default = False
                    r.save()
            except ResourceState.DoesNotExist:
                pass
        super(ResourceState, self).save(*args, **kwargs)

    @classmethod
    def get_default(cls):
        return cls.objects.get(is_default=True)
