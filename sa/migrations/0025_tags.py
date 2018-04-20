# encoding: utf-8
from south.db import db
<<<<<<< HEAD
from noc.core.model.fields import AutoCompleteTagsField
=======
from noc.lib.fields import AutoCompleteTagsField
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

class Migration:
    TAG_MODELS=["sa_activator","sa_managedobject"]
    def forwards(self):
        for m in self.TAG_MODELS:
            db.add_column(m,"tags",AutoCompleteTagsField("Tags",null=True,blank=True))
        db.add_column("sa_managedobjectselector","filter_tags",AutoCompleteTagsField("Tags",null=True,blank=True))

    def backwards(self):
        for m in self.TAG_MODELS:
            db.delete_column(m,"tags")
        db.delete_column("sa_managedobjectselector","filter_tags")
