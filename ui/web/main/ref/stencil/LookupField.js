//---------------------------------------------------------------------
// NOC.main.ref.stencil.LookupField
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug('Defining NOC.main.ref.stencil.LookupField');

Ext.define('NOC.main.ref.stencil.LookupField', {
    extend: 'NOC.core.LookupField',
    alias: 'widget.main.ref.stencil.LookupField',
    tpl: '<tpl for="."><div class="x-boundlist-item"><img src="/ui/pkg/stencils/{id}.svg" style="width: 32px;height: 32px"/> {label}</div></tpl>',
    uiStyle: 'medium'
});
