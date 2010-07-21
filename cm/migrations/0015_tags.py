# encoding: utf-8
from south.db import db
from noc.lib.fields import AutoCompleteTagsField

class Migration:
    TAG_MODELS=["cm_objectnotify"]
    def forwards(self):
        for m in self.TAG_MODELS:
            db.add_column(m,"tags",AutoCompleteTagsField("Tags",null=True,blank=True))

    def backwards(self):
        for m in self.TAG_MODELS:
            db.delete_column(m,"tags")
