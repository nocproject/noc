# -*- coding: utf-8 -*-

from south.db import db
from django.db import models

class Migration:
<<<<<<< HEAD

    def forwards(self):
        VCFilter = db.mock_model(model_name='VCFilter', db_table='vc_vcfilter', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)        
        db.add_column("vc_vcdomainprovisioningconfig","vc_filter",models.ForeignKey(VCFilter,verbose_name="VC Filter",null=True,blank=True))    

=======
    
    def forwards(self):
        VCFilter = db.mock_model(model_name='VCFilter', db_table='vc_vcfilter', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)        
        db.add_column("vc_vcdomainprovisioningconfig","vc_filter",models.ForeignKey(VCFilter,verbose_name="VC Filter",null=True,blank=True))    
    
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    def backwards(self):
        db.drop_column("vc_vcdomainprovisioningconfig","vc_filter")
