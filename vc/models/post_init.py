# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## VC module post-initialization
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Django modules
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
## NOC modules
from sa.models.selectorcache import SelectorCache
from vcdomain import VCDomain

##
## Managed Object subscribers
##
@receiver(post_save, sender=VCDomain)
def on_save(sender, instance, created, **kwargs):
    SelectorCache.refresh()


@receiver(pre_delete, sender=VCDomain)
def on_delete(sender, instance, **kwargs):
    SelectorCache.refresh()
