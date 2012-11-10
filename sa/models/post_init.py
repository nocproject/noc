# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## SA module post-initialization
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
## NOC modules
from selectorcache import SelectorCache
from managedobject import ManagedObject
from managedobjectselector import ManagedObjectSelector

##
## Managed Object subscribers
##
@receiver(post_save, sender=ManagedObject)
def mo_change_update_selector_cache(sender, instance, created, **kwargs):
    print "BLAT!"
    SelectorCache.refresh()


@receiver(pre_delete, sender=ManagedObject)
def mo_delete_update_selector_cache(sender, instance, **kwargs):
    SelectorCache.refresh()

##
## Managed Object Selector subscribers
##
@receiver(post_save, sender=ManagedObjectSelector)
def mos_change_update_selector_cache(sender, instance, created, **kwargs):
    SelectorCache.refresh()


@receiver(pre_delete, sender=ManagedObjectSelector)
def mos_delete_update_selector_cache(sender, instance, **kwargs):
    SelectorCache.refresh()
