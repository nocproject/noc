# encoding: utf-8
from south.db import db
from noc.lib.fields import AutoCompleteTagsField
from django.contrib.contenttypes.management import update_contenttypes
import noc.sa.models

class Migration:
    depends_on=(
        ("cm","0016_no_objectgroup"),
    )
    def forwards(self):
        # Update content types to last actual state
        update_contenttypes(noc.sa.models,None)
        # Convert groups to tags
        ctype_id=db.execute("SELECT id FROM django_content_type WHERE model='managedobject'")[0][0]
        for category,entry_id in db.execute("SELECT g.name,o.managedobject_id FROM sa_managedobject_groups o JOIN sa_objectgroup g ON (o.objectgroup_id=g.id)"):
            if db.execute("SELECT COUNT(*) FROM tagging_tag WHERE name=%s",[category])[0][0]==0:
                db.execute("INSERT INTO tagging_tag(name) VALUES(%s)",[category])
            tag_id=db.execute("SELECT id FROM tagging_tag WHERE name=%s",[category])[0][0]
            db.execute("INSERT INTO tagging_taggeditem(tag_id,content_type_id,object_id) VALUES(%s,%s,%s)",[tag_id,ctype_id,entry_id])        
        # Drop groups and fields
        for t in ["sa_managedobject_groups","sa_managedobjectselector_filter_groups","sa_objectgroup"]:
            db.drop_table(t)

    def backwards(self):
        pass
