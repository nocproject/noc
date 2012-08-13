# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Models for DNS module
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
import os
import time
import subprocess
# Django modules
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models import Q
# NOC Modules
from noc.settings import config
from noc.main.models import NotificationGroup
from noc.ip.models import Address, AddressRange
from noc.lib.validators import is_ipv4, check_re
from noc.lib.fileutils import is_differ, rewrite_when_differ, safe_rewrite
from noc.dns.generators import generator_registry
from noc.lib.rpsl import rpsl_format
from noc.lib.fields import AutoCompleteTagsField
from noc.lib.app.site import site
from noc.lib.ip import *

from dnsserver import DNSServer, generator_registry
from dnszoneprofile import DNSZoneProfile
from dnszone import DNSZone
from dnszonerecordtype import DNSZoneRecordType
from dnszonerecord import DNSZoneRecord