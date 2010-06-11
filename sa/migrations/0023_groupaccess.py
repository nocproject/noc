# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.sa.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'GroupAccess'
        db.create_table('sa_groupaccess', (
            ('id', orm['sa.GroupAccess:id']),
            ('group', orm['sa.GroupAccess:group']),
            ('selector', orm['sa.GroupAccess:selector']),
        ))
        db.send_create_signal('sa', ['GroupAccess'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'GroupAccess'
        db.delete_table('sa_groupaccess')
        
    
    
    models = {
        'auth.group': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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
        'sa.groupaccess': {
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'selector': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sa.ManagedObjectSelector']"})
        },
        'sa.managedobject': {
            'activator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sa.Activator']"}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'administrative_domain': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sa.AdministrativeDomain']"}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sa.ObjectGroup']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_configuration_managed': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_managed': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'port': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'profile_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'remote_path': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'repo_path': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'scheme': ('django.db.models.fields.IntegerField', [], {}),
            'snmp_ro': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'snmp_rw': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'super_password': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'trap_community': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'trap_source_ip': ('INETField', ['"Trap Source IP"'], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'})
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
        'sa.maptask': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'managed_object': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sa.ManagedObject']"}),
            'map_script': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'next_try': ('django.db.models.fields.DateTimeField', [], {}),
            'retries_left': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'script_params': ('PickledField', ['"Params"'], {'null': 'True', 'blank': 'True'}),
            'script_result': ('PickledField', ['"Result"'], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'W'", 'max_length': '1'}),
            'task': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sa.ReduceTask']"})
        },
        'sa.objectgroup': {
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        'sa.reducetask': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reduce_script': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'script_params': ('PickledField', ['"Params"'], {'null': 'True', 'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'stop_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'sa.taskschedule': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'next_run': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'periodic_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'retries': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'retries_left': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'retry_delay': ('django.db.models.fields.PositiveIntegerField', [], {'default': '60'}),
            'run_every': ('django.db.models.fields.PositiveIntegerField', [], {'default': '86400'}),
            'timeout': ('django.db.models.fields.PositiveIntegerField', [], {'default': '300'})
        },
        'sa.useraccess': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'selector': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sa.ManagedObjectSelector']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }
    
    complete_apps = ['sa']
