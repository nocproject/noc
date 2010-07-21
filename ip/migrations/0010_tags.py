# encoding: utf-8
from south.db import db
from noc.ip.models import *
from noc.lib.fields import AutoCompleteTagsField

class Migration:
    TAG_MODELS=["ip_vrf","ip_ipv4block","ip_ipv4address"]
    def forwards(self):
        for m in self.TAG_MODELS:
            db.add_column(m,"tags",AutoCompleteTagsField("Tags",null=True,blank=True))

    def backwards(self):
        for m in self.TAG_MODELS:
            db.delete_column(m,"tags")
