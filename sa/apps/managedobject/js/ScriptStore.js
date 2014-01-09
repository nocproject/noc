//---------------------------------------------------------------------
// sa.managedobject Script Store
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.ScriptStore");

Ext.define("NOC.sa.managedobject.ScriptStore", {
    extend: "Ext.data.Store",
    model: null,
    fields: [
        {
            name: "name",
            type: "string"
        },
        {
            name: "has_input",
            type: "boolean"
        },
        {
            name: "require_input",
            type: "boolean"
        },
        {
            name: "form",
            type: "auto"
        },
        {
            name: "preview",
            type: "string"
        }
    ],
    data: []
});
