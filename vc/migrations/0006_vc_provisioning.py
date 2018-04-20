# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from django.db import models

class Migration:
    depends_on = [
        ("sa", "0015_managedobjectselector")
    ]
<<<<<<< HEAD

    def forwards(self):
        VCDomain = db.mock_model(model_name='VCDomain', db_table='vc_vcdomain', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        ManagedObjectSelector = db.mock_model(model_name='ManagedObjectSelector', db_table='sa_managedobjectselector', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)

=======
    
    def forwards(self):
        VCDomain = db.mock_model(model_name='VCDomain', db_table='vc_vcdomain', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        ManagedObjectSelector = db.mock_model(model_name='ManagedObjectSelector', db_table='sa_managedobjectselector', db_tablespace='', pk_field_name='id', pk_field_type=models.AutoField)
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Adding model 'VCDomainProvisioningConfig'
        db.create_table('vc_vcdomainprovisioningconfig', (
            ('id', models.AutoField(primary_key=True)),
            ('vc_domain', models.ForeignKey(VCDomain, verbose_name="VC Domain")),
            ('selector', models.ForeignKey(ManagedObjectSelector, verbose_name="Managed Object Selector")),
            ('key', models.CharField("Key", max_length=64)),
            ('value', models.CharField("Value", max_length=256)),
        ))
        db.send_create_signal('vc', ['VCDomainProvisioningConfig'])
<<<<<<< HEAD

        # Creating unique_together for [vc_domain, selector, key] on VCDomainProvisioningConfig.
        db.create_unique('vc_vcdomainprovisioningconfig', ['vc_domain_id', 'selector_id', 'key'])

        db.add_column("vc_vcdomain","enable_provisioning",models.BooleanField("Enable Provisioning",default=False))

    def backwards(self):

        # Deleting model 'VCDomainProvisioningConfig'
        db.delete_table('vc_vcdomainprovisioningconfig')

        # Deleting unique_together for [vc_domain, selector, key] on VCDomainProvisioningConfig.
        db.delete_unique('vc_vcdomainprovisioningconfig', ['vc_domain_id', 'selector_id', 'key'])
=======
        
        # Creating unique_together for [vc_domain, selector, key] on VCDomainProvisioningConfig.
        db.create_unique('vc_vcdomainprovisioningconfig', ['vc_domain_id', 'selector_id', 'key'])
        
        db.add_column("vc_vcdomain","enable_provisioning",models.BooleanField("Enable Provisioning",default=False))
    
    def backwards(self):
        
        # Deleting model 'VCDomainProvisioningConfig'
        db.delete_table('vc_vcdomainprovisioningconfig')
        
        # Deleting unique_together for [vc_domain, selector, key] on VCDomainProvisioningConfig.
        db.delete_unique('vc_vcdomainprovisioningconfig', ['vc_domain_id', 'selector_id', 'key'])
        
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
