//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------

console.debug('Defining NOC.sa.managedobject.store.Template');
Ext.define('NOC.sa.managedobject.store.Template', {
    extend: 'Ext.data.Model',
    fields: ['name'],
    proxy: {
        type: 'localstorage',
        id: 'sa-managedobject-template'
    }
});