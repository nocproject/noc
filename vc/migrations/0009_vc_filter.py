# -*- coding: utf-8 -*-

from south.db import db
from django.db import models

class Migration:
<<<<<<< HEAD

    def forwards(self):

=======
    
    def forwards(self):
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Adding model 'VCFilter'
        db.create_table('vc_vcfilter', (
            ('id', models.AutoField(primary_key=True)),
            ('name', models.CharField("Name", unique=True, max_length=64)),
            ('expression', models.CharField("Expression", max_length=256)),
            ('description', models.TextField("Description", null=True, blank=True)),
        ))
        db.send_create_signal('vc', ['VCFilter'])
        # Add "Any VLAN filter"
        if db.execute("SELECT COUNT(*) FROM vc_vcfilter WHERE name='Any VLAN'")[0][0]==0:
            db.execute("INSERT INTO vc_vcfilter(name,expression) VALUES(%s,%s)",["Any VLAN","1-4095"])
<<<<<<< HEAD

    def backwards(self):

=======
    
    def backwards(self):
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Deleting model 'VCFilter'
        db.delete_table('vc_vcfilter')
