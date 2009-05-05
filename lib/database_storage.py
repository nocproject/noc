# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Database File Storage (PostgreSQL only)
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
from django.core.files.storage import Storage
from django.core.files.base import File,ContentFile
from django.conf import settings
import psycopg2
##
## Database File Storage (PostgreSQL)
## Stores files in database table.
## Table must have at least following columns:
##   File Name (Character Type) - contains full virtual path
##   Binary Data (BYTEA) - File content
##   Size (Integer Type) - File size (in octets)
##   Modification Time (Timestamp) - Last modification time
## Table name and field names must be set up via
## "option" variable. "option" is a hash with following keys:
##   db_table
##   name_field
##   data_field
##   size field
##   mtime_field
##
class DatabaseStorage(Storage):
    def __init__(self,option):
        self.db_table    = option["db_table"]
        self.name_field  = option["name_field"]
        self.data_field  = option["data_field"]
        self.size_field  = option["size_field"]
        self.mtime_field = option["mtime_field"]
    ##
    ##
    ##
    def get_cursor(self):
        from django.db import connection
        return connection.cursor()
    ##
    ## Internal implementation of the open()
    ##   name - is a full path
    ##   mode - is a file mode (ignored)
    ## Returns File object or None
    ##
    def _open(self, name, mode="rb"):
        cursor=self.get_cursor()
        cursor.execute("SELECT %s FROM %s WHERE %s=%%s"%(self.data_field,self.db_table,self.name_field),[name])
        row=cursor.fetchone()
        if row is None:
            return None
        return ContentFile(row[0])
    ##
    ## Internal implementation of save()
    ##   name - is a full path
    ##   content - is a File object
    ## Returns file name
    ##
    def _save(self, name, content):
        cursor=self.get_cursor()
        binary=content.read()
        size=len(binary)
        binary=psycopg2.Binary(binary)
        if self.exists(name):
            cursor.execute("UPDATE %s SET %s=%%s,%s='now',%s=%%s WHERE %s=%%s"%(self.db_table,self.data_field,
                    self.mtime_field,self.size_field,self.name_field),[binary,size,name])
        else:
            cursor.execute("INSERT INTO %s(%s,%s,%s,%s) VALUES(%%s,'now',%%s,%%s)"%(self.db_table,self.name_field,
                self.mtime_field,self.size_field,self.data_field),[name,size,binary])
        return name
    ##
    ## Check a file exists
    ##   name - is a full path
    ## Returns boolean
    ##
    def exists(self,name):
        cursor=self.get_cursor()
        cursor.execute("SELECT COUNT(*) FROM %s WHERE %s=%%s"%(self.db_table,self.name_field),[name])
        return cursor.fetchone()[0]>0
    ##
    ## Returns full filesystem path as specified in Storage API
    ## Raises NotImplementedError because Storage is not related to filesystem
    ##
    def path(self,name):
        raise NotImplementedError
    ##
    ## Returns file size or 0
    ##
    def size(self,name):
        cursor=self.get_cursor()
        cursor.execute("SELECT %s FROM %s WHERE %s=%%s"%(self.size_field,self.db_table,self.name_field),[name])
        row=cursor.fetchone()
        if row:
            return row[0]
        else:
            return 0
    ##
    ##
    ##
    def url(self,name):
        pass
    ##
    ## Deletes file
    ##    name is a full path
    ##
    def delete(self,name):
        cursor=self.get_cursor()
        cursor.execute("DELETE FROM %s WHERE %s=%%s"%(self.db_table,self.name_field),[name])
    ##
    ## Returns converted file name (Required by Storage API)
    ##
    def get_available_name(self,name):
        return name
    ##
    ## Returns a directory listing
    ##   name - is a full path of directory
    ## Returns empty list when directory does not exists
    ##
    def listdir(self,name):
        cursor=self.get_cursor()
        if not name.endswith("/"):
            name+="/"
        ln=len(name)
        cursor.execute("SELECT %s FROM %s WHERE %s ~ '^%s[^/]+/?$'"%(self.name_field,self.db_table,self.name_field,name.replace("'","\\'")))
        return [x[0][ln:] for x in cursor.fetchall()]
    ##
    ## Returns file stats.
    ## stats is a hash of
    ##    name  : full path
    ##    size  : file size
    ##    mtime : last modification time
    ## Returns None when file does not exists
    def stat(self,name):
        cursor=self.get_cursor()
        cursor.execute("SELECT %s,%s FROM %s WHERE %s=%%s"%(self.size_field,self.mtime_field,self.db_table,self.name_field),[name])
        row=cursor.fetchone()
        if row:
            return {
                "name" : "name",
                "size" : row[0],
                "mtime": row[1],
            }
        else:
            return None
    ##
    ## Set file's mtime
    ##
    def set_mtime(self,name,mtime):
        cursor=self.get_cursor()
        cursor.execute("UPDATE %s SET %s=%%s WHERE %s=%%s"%(self.db_table,self.mtime_field,self.name_field),[mtime,name])
