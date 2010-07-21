# encoding: utf-8
from south.db import db
from django.contrib.contenttypes.management import update_contenttypes
import noc.cm.models

class Migration:
    def forwards(self):
        # Update content types to last actual state
        update_contenttypes(noc.cm.models,None)
        # Convert groups to tags
        ctype_id=db.execute("SELECT id FROM django_content_type WHERE model='objectnotify' AND app_label='cm'")[0][0]
        for category,entry_id in db.execute("SELECT g.name,o.managedobject_id FROM sa_objectgroup g JOIN sa_managedobject_groups o ON (g.id=o.objectgroup_id)"):
            if db.execute("SELECT COUNT(*) FROM tagging_tag WHERE name=%s",[category])[0][0]==0:
                db.execute("INSERT INTO tagging_tag(name) VALUES(%s)",[category])
            tag_id=db.execute("SELECT id FROM tagging_tag WHERE name=%s",[category])[0][0]
            db.execute("INSERT INTO tagging_taggeditem(tag_id,content_type_id,object_id) VALUES(%s,%s,%s)",[tag_id,ctype_id,entry_id])        
        # Drop groups and fields
        db.drop_column("cm_objectnotify","group_id")

    def backwards(self):
        pass
