//---------------------------------------------------------------------
// Add Interfaces Store
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vc.AddInterfacesStore");

Ext.define("NOC.vc.vc.AddInterfacesStore", {
    extend: "Ext.data.Store",
    fields: [
        "managed_object",
        "managed_object__label",
        "interface",
        "description",
        "error"
         /*,
        "tagged"  // @todo: boolean
        */
    ],
    data: [{}]
});