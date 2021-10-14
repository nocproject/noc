//---------------------------------------------------------------------
// sa.managedobject CapabilitiesModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.CapabilitiesModel");

Ext.define("NOC.sa.managedobject.CapabilitiesModel", {
    extend: "Ext.data.Model",
    rest_url: "/sa/managedobject/{{parent}}/caps/",
    parentField: "managed_object_id",

    fields: [
        {
            name: "capability",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "source",
            type: "string"
        },
        {
            name: "value",
            type: "auto"
        }
    ]
});

