# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Database models for main module
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python Modules
from __future__ import with_statement

import datetime

from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator
from django.db import models
from django.db.models.signals import pre_save, pre_delete,\
                                     post_save, post_delete
from django.utils.translation import ugettext_lazy as _
from noc import settings
from noc.lib.periodic import periodic_registry
from noc.main.refbooks.downloaders import downloader_registry
from noc.main.refbooks.downloaders import downloader_registry
from noc.lib.middleware import get_user, get_request
from noc.lib.timepattern import TimePattern as TP
from noc.lib.timepattern import TimePatternList
from noc.sa.interfaces.base import interface_registry
from noc.lib.app.site import site
from noc.lib.validators import check_extension, check_mimetype
from noc.lib import nosql
from noc.lib.validators import is_int
## Register periodics
from audittrail import AuditTrail
AuditTrail.install()

##
## Initialize download registry
##


# from customfieldenumgroup import CustomFieldEnumGroup
# from customfieldenumvalue import CustomFieldEnumValue
# from customfield import CustomField




# from resourcestate import ResourceState
#from pyrule import PyRule, NoPyRuleException


##
## Search patters
##






# from timepattern import TimePattern
#from timepatternterm import TimePatternTerm


# from notificationgroup import (
#    NotificationGroup, NotificationGroupUser, NotificationGroupOther,
#    )

# from userprofile import UserProfile, UserProfileManager
# from userprofilecontact import UserProfileContact
#from dbtrigger import DBTrigger, model_choices



# from prefixtable import PrefixTable, PrefixTablePrefix
# from template import Template
#from systemtemtemplate import SystemTemplate


# from favorites import Favorites
# from tag import Tag
#from sync import Sync

##
## Install triggers
##

##
## Monkeypatch to change User.username.max_length
##
User._meta.get_field("username").max_length = User._meta.get_field("email").max_length
User._meta.get_field("username").validators = [MaxLengthValidator(User._meta.get_field("username").max_length)]
User._meta.ordering = ["username"]
