//---------------------------------------------------------------------
// NOC.pm.ts.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.ts.TSTypeField");

Ext.define("NOC.pm.ts.TSTypeField", {
    extend: "Ext.form.ComboBox",
    alias: "widget.pm.ts.TSTypeField",
    queryMode: "local",
    displayField: "label",
    valueField: "id",
    store: [
        ["G", "Gauge"],
        ["C", "Counter"],
        ["D", "Derive"]
    ]
});
