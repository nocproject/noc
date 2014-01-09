//---------------------------------------------------------------------
// NOC.sa.managedobject.Lookup
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.SchemeLookupField");

Ext.define("NOC.sa.managedobject.SchemeLookupField", {
    extend: "Ext.form.field.ComboBox",
    alias: "widget.sa.managedobject.SchemeLookupField",
    queryMode: "local",
    valueField: "id",
    displayField: "label",
    store: [
        [0, "TELNET"],
        [1, "SSH"],
        [2, "HTTP"]
    ]
});
