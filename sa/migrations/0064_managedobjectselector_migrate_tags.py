# encoding: utf-8
from noc.core.model.fields import TagsField
from south.db import db


class Migration:
    def forwards(self):
        # Create temporary tags fields
        db.add_column("sa_managedobjectselector", "tmp_filter_tags",
                      TagsField("Tags", null=True, blank=True))
        # Migrate data
        db.execute("""
            UPDATE sa_managedobjectselector
            SET tmp_filter_tags = string_to_array(regexp_replace(filter_tags, ',$', ''), ',')
            WHERE filter_tags != ''
            """)

    def backwards(self):
        pass
