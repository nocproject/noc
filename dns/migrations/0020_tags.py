# encoding: utf-8
from south.db import db
from noc.core.model.fields import AutoCompleteTagsField


class Migration:
    TAG_MODELS = ["dns_dnszone", "dns_dnszonerecord"]

    def forwards(self):
        for m in self.TAG_MODELS:
            db.add_column(m, "tags",
                AutoCompleteTagsField("Tags", null=True, blank=True))

    def backwards(self):
        for m in self.TAG_MODELS:
            db.delete_column(m, "tags")
