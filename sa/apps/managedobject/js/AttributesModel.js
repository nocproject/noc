//---------------------------------------------------------------------
// sa.managedobject AttributesModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.AttributesModel");

Ext.define("NOC.sa.managedobject.AttributesModel", {
    extend: "Ext.data.Model",
    rest_url: "/sa/managedobject/{{parent}}/attrs/",
    parentField: "managed_object_id",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "key",
            type: "string"
        },
        {
            name: "value",
            type: "string"
        }
    ]
});

