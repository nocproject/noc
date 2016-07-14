//---------------------------------------------------------------------
// NOC.main.ref.stencil.LookupField
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.ref.stencil.LookupField");

Ext.define("NOC.main.ref.stencil.LookupField", {
    extend: "NOC.core.LookupField",
    alias: "widget.main.ref.stencil.LookupField",
    listConfig: {
        tpl: '<tpl for="."><div class="x-boundlist-item"><img src="/inv/map/stencils/{id}/" style="width: 32px;height: 32px"/> {label}</div></tpl>',
        minWidth: 240
    },
    uiStyle: "medium"
});
