# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## CSV import/export utilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
import csv,cStringIO
from django.db import models
##
##
##
def get_model_fields(model):
    # Detect fields
    fields=[]
    for f in model._meta.fields:
        if f.name=="id":
            continue
        required=not f.null and f.default==models.fields.NOT_PROVIDED
        # Process references
        if f.rel:
            if isinstance(f.rel,models.fields.related.ManyToOneRel):
                # Foreign Key
                # Try to find unique key
                k="id"
                for ff in f.rel.to._meta.fields:
                    if ff.name!="id" and ff.unique:
                        k=ff.name
                        break
                fields+=[(f.name,required,f.rel.to,k)]
        else:
            fields+=[(f.name,required,None,None)]
    return fields
##
## Export to CSV
##
def csv_export(model,queryset=None):
    io=cStringIO.StringIO()
    writer=csv.writer(io)
    fields=get_model_fields(model)
    # Write header
    writer.writerow([f[0] for f in fields])
    # Build queryset
    if queryset is None:
        queryset=model.objects.all()
    # Write rows
    for r in queryset:
        row=[]
        # Format row
        for f,required,rel,rf in fields:
            v=getattr(r,f)
            if v is None:
                v=""
            if rel is None or not v:
                row+=[v]
            else:
                row+=[getattr(v,rf)]
        row=[unicode(f).encode("utf-8") for f in row]
        writer.writerow(row)
    # Return result
    return io.getvalue()
##
## Import from CSV
## returns (record_count,error_message)
## record count must be None, if error_message set
##
IGNORED_REQUIRED={
    "ip_address" : set(["prefix"]),
}
def csv_import(model,f):
    reader=csv.reader(f)
    # Process model fields
    field_names=set()
    required_fields=set()
    fk={} # Foreign keys: name->(model,field)
    booleans=set() # Boolean fields:
    # Try to find index field
    index_field="id"
    for f in model._meta.fields:
        if f.name!=index_field and f.unique:
            index_field=f.name
            break
    # find boolean fields
    booleans=set([f.name for f in model._meta.fields if isinstance(f,models.BooleanField)])
    # Search for foreign keys and required fields
    ir=IGNORED_REQUIRED.get(model._meta.db_table,set())
    for name,required,rel,rname in get_model_fields(model):
        field_names.add(name)
        if rel:
            fk[name]=(rel,rname)
        if required and not name in ir:
            required_fields.add(name)
    # Read and validate header
    header=reader.next()
    left=field_names.copy()
    # Check field names
    for h in header:
        if h not in field_names:
            return None,"Invalid field '%s'"%h
        left.remove(h)
    # Chek all required fields present
    for h in left:
        if h in required_fields:
            return None,"Required field '%s' is missed"%h
    # Load data
    count=1
    l_header=len(header)
    for row in reader:
        if len(row)!=l_header:
            return None,"Invalid row size. line %d"%count
        vars=dict(zip(header,row))
        for h,v in vars.items():
            # Check required field is not none
            if not v and h in required_fields:
                return None,"Required field '%s' is empty at line %d"%(h,count)
            # Delete empty values
            if not v:
                del vars[h]
            # reference foreign keys
            if h in fk and v:
                rel,rname=fk[h]
                try:
                    ro=rel.objects.get(**{rname:v})
                except rel.DoesNotExist:
                    # Failed to reference by name, fallback to id
                    try:
                        id=int(v)
                    except:
                        return None,"Cannot resolve '%s' in field '%s' at line '%s'"%(v,h,count)
                    try:
                        ro=rel.objects.get(**{"id":id})
                    except rel.DoesNotExist:
                        return None,"Cannot resolve '%s' in field '%s' at line '%s'"%(v,h,count)
                vars[h]=ro
        # Load or create new object
        if index_field!="id":
            try:
                o=model.objects.get(**{index_field:vars[index_field]})
            except model.DoesNotExist:
                o=model()
        else:
            o=model()
        # Set attributes
        for k,v in vars.items():
            if k in booleans:
                # Convert boolean
                v=v.lower() in ["t","true","yes","y"]
            setattr(o,k,v)
        # Save
        try:
            o.save()
            count+=1
        except Exception,why:
            return None,"Failed to save line %d: %s"%(count,str(why))
    return count-1,None