# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.vc.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'VCBindFilter'
        db.create_table('vc_vcbindfilter', (
            ('id', orm['vc.VCBindFilter:id']),
            ('vc_domain', orm['vc.VCBindFilter:vc_domain']),
            ('vrf', orm['vc.VCBindFilter:vrf']),
            ('prefix', orm['vc.VCBindFilter:prefix']),
            ('vc_filter', orm['vc.VCBindFilter:vc_filter']),
        ))
        db.send_create_signal('vc', ['VCBindFilter'])
        
        # Adding field 'VCDomain.enable_vc_bind_filter'
        db.add_column('vc_vcdomain', 'enable_vc_bind_filter', orm['vc.VCDomain:enable_vc_bind_filter'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'VCBindFilter'
        db.delete_table('vc_vcbindfilter')
        
        # Deleting field 'VCDomain.enable_vc_bind_filter'
        db.delete_column('vc_vcdomain', 'enable_vc_bind_filter')
        
    
    
    models = {
        'ip.vrf': {
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'rd': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '21'}),
            'tt': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'vrf_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ip.VRFGroup']"})
        },
        'ip.vrfgroup': {
            'description': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'unique_addresses': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'main.notificationgroup': {
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'sa.activator': {
            'auth': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'to_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'})
        },
        'sa.administrativedomain': {
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        'sa.managedobjectselector': {
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'filter_activator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sa.Activator']", 'null': 'True', 'blank': 'True'}),
            'filter_address': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'filter_administrative_domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sa.AdministrativeDomain']", 'null': 'True', 'blank': 'True'}),
            'filter_description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'filter_groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sa.ObjectGroup']", 'null': 'True', 'blank': 'True'}),
            'filter_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'filter_name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'filter_profile': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'filter_remote_path': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'filter_repo_path': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'filter_user': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'source_combine_method': ('django.db.models.fields.CharField', [], {'default': "'O'", 'max_length': '1'}),
            'sources': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['sa.ManagedObjectSelector']", 'null': 'True', 'blank': 'True'})
        },
        'sa.objectgroup': {
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        'vc.vc': {
            'Meta': {'unique_together': "[('vc_domain', 'l1', 'l2'), ('vc_domain', 'name')]"},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'l1': ('django.db.models.fields.IntegerField', [], {}),
            'l2': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'vc_domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vc.VCDomain']"})
        },
        'vc.vcbindfilter': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prefix': ('CIDRField', ['"prefix"'], {}),
            'vc_domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vc.VCDomain']"}),
            'vc_filter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vc.VCFilter']"}),
            'vrf': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['ip.VRF']"})
        },
        'vc.vcdomain': {
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'enable_provisioning': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'enable_vc_bind_filter': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vc.VCType']"})
        },
        'vc.vcdomainprovisioningconfig': {
            'Meta': {'unique_together': "[('vc_domain', 'selector')]"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'notification_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.NotificationGroup']", 'null': 'True', 'blank': 'True'}),
            'selector': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sa.ManagedObjectSelector']"}),
            'tagged_ports': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'vc_domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vc.VCDomain']"}),
            'vc_filter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['vc.VCFilter']", 'null': 'True', 'blank': 'True'})
        },
        'vc.vcfilter': {
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'expression': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'vc.vctype': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label1_max': ('django.db.models.fields.IntegerField', [], {}),
            'label1_min': ('django.db.models.fields.IntegerField', [], {}),
            'label2_max': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'label2_min': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'min_labels': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        }
    }
    
    complete_apps = ['vc']
