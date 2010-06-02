# -*- coding: utf-8 -*-

from south.db import db
from django.db import models
from noc.main.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Permission'
        db.create_table('main_permission', (
            ('id', orm['main.Permission:id']),
            ('name', orm['main.Permission:name']),
        ))
        db.send_create_signal('main', ['Permission'])
        
        # Adding ManyToManyField 'Permission.groups'
        db.create_table('main_permission_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('permission', models.ForeignKey(orm.Permission, null=False)),
            ('group', models.ForeignKey(orm['auth.Group'], null=False))
        ))
        
        # Adding ManyToManyField 'Permission.users'
        db.create_table('main_permission_users', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('permission', models.ForeignKey(orm.Permission, null=False)),
            ('user', models.ForeignKey(orm['auth.User'], null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Permission'
        db.delete_table('main_permission')
        
        # Dropping ManyToManyField 'Permission.groups'
        db.delete_table('main_permission_groups')
        
        # Dropping ManyToManyField 'Permission.users'
        db.delete_table('main_permission_users')
        
    
    
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
        'main.audittrail': {
            'body': ('django.db.models.fields.TextField', [], {}),
            'db_table': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'operation': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'main.databasestorage': {
            'data': ('BinaryField', ['"Data"'], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256'}),
            'size': ('django.db.models.fields.IntegerField', [], {})
        },
        'main.language': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'native_name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'main.mimetype': {
            'extension': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '63'})
        },
        'main.notification': {
            'actual_till': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'next_try': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'notification_method': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'notification_params': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        'main.notificationgroup': {
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'main.notificationgroupother': {
            'Meta': {'unique_together': "[('notification_group', 'time_pattern', 'notification_method', 'params')]"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notification_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.NotificationGroup']"}),
            'notification_method': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'params': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'time_pattern': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.TimePattern']"})
        },
        'main.notificationgroupuser': {
            'Meta': {'unique_together': "[('notification_group', 'time_pattern', 'user')]"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notification_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.NotificationGroup']"}),
            'time_pattern': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.TimePattern']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'main.permission': {
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']"})
        },
        'main.pyrule': {
            'changed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interface': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'main.refbook': {
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'download_url': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'downloader': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_builtin': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Language']"}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'next_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'refresh_interval': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'main.refbookdata': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ref_book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.RefBook']"}),
            'value': ('TextArrayField', ['"Value"'], {})
        },
        'main.refbookfield': {
            'Meta': {'unique_together': "[('ref_book', 'order'), ('ref_book', 'name')]"},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_required': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': "'64'"}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'ref_book': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.RefBook']"}),
            'search_method': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        'main.systemnotification': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'notification_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.NotificationGroup']", 'null': 'True', 'blank': 'True'})
        },
        'main.timepattern': {
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        },
        'main.timepatternterm': {
            'Meta': {'unique_together': "[('time_pattern', 'term')]"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'term': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'time_pattern': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.TimePattern']"})
        },
        'main.userprofile': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preferred_language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Language']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'main.userprofilecontact': {
            'Meta': {'unique_together': "[('user_profile', 'time_pattern', 'notification_method', 'params')]"},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notification_method': ('django.db.models.fields.CharField', [], {'max_length': '16'}),
            'params': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'time_pattern': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.TimePattern']"}),
            'user_profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.UserProfile']"})
        }
    }
    
    complete_apps = ['main']
