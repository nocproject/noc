//---------------------------------------------------------------------
// VC Import Store
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vc.VCImportStore");

Ext.define("NOC.vc.vc.VCImportStore", {
    extend: "Ext.data.Store",
    fields: [
        "label",
        "l1",
        "l2",
        "name",
        "description"
    ]
});