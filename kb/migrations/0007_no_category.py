# encoding: utf-8
from south.db import db
from django.contrib.contenttypes.management import update_contenttypes
import noc.kb.models

class Migration:
    def forwards(self):
        # Update content types to last actual state
        update_contenttypes(noc.kb.models,None)
        # Migrate tags
        ctype_id=db.execute("SELECT id FROM django_content_type WHERE model='kbentry'")[0][0]
        for category,entry_id in db.execute("SELECT c.name,e.kbentry_id FROM kb_kbentry_categories e JOIN kb_kbcategory c ON (e.kbcategory_id=c.id)"):
            category=category[:49]
            if db.execute("SELECT COUNT(*) FROM tagging_tag WHERE name=%s",[category])[0][0]==0:
                db.execute("INSERT INTO tagging_tag(name) VALUES(%s)",[category])
            tag_id=db.execute("SELECT id FROM tagging_tag WHERE name=%s",[category])[0][0]
            db.execute("INSERT INTO tagging_taggeditem(tag_id,content_type_id,object_id) VALUES(%s,%s,%s)",[tag_id,ctype_id,entry_id])
        db.delete_table("kb_kbentrytemplate_categories")
        db.delete_table("kb_kbentry_categories")
        db.delete_table("kb_kbcategory")

    def backwards(self):
        pass
