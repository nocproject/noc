//---------------------------------------------------------------------
// VC Import Store
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vc.VCImportStore");

Ext.define("NOC.vc.vc.VCImportStore", {
    extend: "Ext.data.Store",
    model: null,
    fields: [
        {
            name: "label",
            type: "string"
        },
        {
            name: "l1",
            type: "int"
        },
        {
            name: "l2",
            type: "int"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        }
    ],
    data: []
});
