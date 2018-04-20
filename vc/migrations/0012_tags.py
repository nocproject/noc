# encoding: utf-8
<<<<<<< HEAD

# Third-party modules
from south.db import db
# NOC modules
from noc.core.model.fields import AutoCompleteTagsField


class Migration(object):
    TAG_MODELS = ["vc_vc"]

    def forwards(self):
        for m in self.TAG_MODELS:
            db.add_column(m, "tags",
                          AutoCompleteTagsField("Tags", null=True,
                                                blank=True))

    def backwards(self):
        for m in self.TAG_MODELS:
            db.delete_column(m, "tags")
=======
from south.db import db
from noc.ip.models import *
from noc.lib.fields import AutoCompleteTagsField

class Migration:
    TAG_MODELS=["vc_vc"]
    def forwards(self):
        for m in self.TAG_MODELS:
            db.add_column(m,"tags",AutoCompleteTagsField("Tags",null=True,blank=True))

    def backwards(self):
        for m in self.TAG_MODELS:
            db.delete_column(m,"tags")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
