# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.vc.models import *

class Migration:
    depends_on = [
        ("ip", "0001_initial")
    ]
    def forwards(self):
        # Adding model 'VCBindFilter'
        VCDomain=db.mock_model(model_name="VCDomain",db_table="vc_vcdomain")
        VRF=db.mock_model(model_name="VRF",db_table="ip_vrf")
        VCFilter=db.mock_model(model_name="VCFilter",db_table="vc_vcfilter")
        db.create_table('vc_vcbindfilter', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('vc_domain', models.ForeignKey(VCDomain,verbose_name="VC Domain")),
            ('vrf', models.ForeignKey(VRF,verbose_name="VRF")),
            ('prefix', CIDRField("Prefix")),
            ('vc_filter', models.ForeignKey(VCFilter,verbose_name="VC Filter")),
        ))
        db.send_create_signal('vc', ['VCBindFilter'])
        
        # Adding field 'VCDomain.enable_vc_bind_filter'
        db.add_column('vc_vcdomain', 'enable_vc_bind_filter', models.BooleanField("Enable VC Bind filter",default=False))
    
    def backwards(self):
        # Deleting model 'VCBindFilter'
        db.delete_table('vc_vcbindfilter')
        # Deleting field 'VCDomain.enable_vc_bind_filter'
        db.delete_column('vc_vcdomain', 'enable_vc_bind_filter')
