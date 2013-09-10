//---------------------------------------------------------------------
// sa.managedobject LAG Store
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.LAGStore");

Ext.define("NOC.sa.managedobject.LAGStore", {
    extend: "Ext.data.Store",
    model: null,
    fields: [
        {
            name: "name",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "members",
            type: "auto"
        },
        {
            name: "count",
            convert: function(value, record) {
                return record.get("members").length;
            }
        }
    ],
    data: []
});
