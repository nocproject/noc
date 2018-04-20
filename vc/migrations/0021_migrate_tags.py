# encoding: utf-8
from south.db import db
<<<<<<< HEAD
from noc.core.model.fields import TagsField
=======
from noc.lib.fields import TagsField
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce


class Migration:
    TAG_MODELS = ["vc_vc"]

    def forwards(self):
        # Create temporary tags fields
        for m in self.TAG_MODELS:
            db.add_column(
                m, "tmp_tags", TagsField("Tags", null=True, blank=True))
        # Migrate data
        for m in self.TAG_MODELS:
            db.execute("""
            UPDATE %s
            SET tmp_tags = string_to_array(regexp_replace(tags, ',$', ''), ',')
            WHERE tags != ''
            """ % m)

    def backwards(self):
        pass
