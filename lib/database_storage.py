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
        assert 
        self.db_table    = option["db_table"]
        self.name_field  = option["name_field"]
        self.data_field  = option["data_field"]
        self.size_field  = option["size_field"]
        self.mtime_field = option["mtime_field"]
        from django.db import connection
        self.cursor=connection.cursor()
    ##
    ## Internal implementation of the open()
    ##   name - is a full path
    ##   mode - is a file mode (ignored)
    ## Returns File object or None
    ##
    def _open(self, name, mode="rb"):
        self.cursor.execute("SELECT %s FROM %s WHERE %s=%%s"%(self.data_field,self.db_table,self.name_field),[name])
        row=self.cursor.fetchone()
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
        binary=content.read()
        size=len(binary)
        binary=psycopg2.Binary(binary)
        if self.exists(name):
            self.cursor.execute("UPDATE %s SET %s=%%s,%s='now',%s=%%s WHERE %s=%%s"%(self.db_table,self.data_field,
                    self.mtime_field,self.size_field,self.name_field),[binary,size,name])
        else:
            self.cursor.execute("INSERT INTO %s(%s,%s,%s,%s) VALUES(%%s,'now',%%s,%%s)"%(self.db_table,self.name_field,
                self.mtime_field,self.size_field,self.data_field),[name,size,binary])
        return name
    ##
    ## Check a file exists
    ##   name - is a full path
    ## Returns boolean
    ##
    def exists(self,name):
        self.cursor.execute("SELECT COUNT(*) FROM %s WHERE %s=%%s"%(self.db_table,self.name_field),[name])
        return self.cursor.fetchone()[0]>0
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
        self.cursor.execute("SELECT %s FROM %s WHERE %s=%%s"%(self.size_field,self.db_table,self.name_field),[name])
        row=self.cursor.fetchone()
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
        self.cursor.execute("DELETE FROM %s WHERE %s=%%s"%(self.db_table,self.name_field),[name])
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
        if not name.endswith("/"):
            name+="/"
        ln=len(name)
        self.cursor.execute("SELECT %s FROM %s WHERE %s ~ '^%s[^/]+/?$'"%(self.name_field,self.db_table,self.name_field,name.replace("'","\\'")))
        return [x[0][ln:] for x in self.cursor.fetchall()]
