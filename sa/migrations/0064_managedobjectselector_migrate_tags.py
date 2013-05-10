# encoding: utf-8
from south.db import db
from noc.lib.fields import TagsField


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
