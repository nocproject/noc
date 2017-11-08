# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Subscriner loader
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import operator

## Third-party modules
import cachetools
from noc.crm.models.subscriber import Subscriber
from noc.crm.models.subscriberprofile import SubscriberProfile

## NOC modules
from base import BaseLoader


class SubscriberLoader(BaseLoader):
    """
    Administrative division loader
    """
    name = "subscriber"
    model = Subscriber
    fields = [
        "id",
        "name",
        "description",
        "profile",
        "address",
        "tech_contact_person",
        "tech_contact_phone"
    ]

    _profile_cache = {}

    @cachetools.cachedmethod(operator.attrgetter("_profile_cache"))
    def get_profile(self, name):
        return SubscriberProfile.objects.get(name=name)

    def clean(self, row):
        d = super(SubscriberLoader, self).clean(row)
        if "profile" in d:
            d["profile"] = self.get_profile(d["profile"])
        return d
