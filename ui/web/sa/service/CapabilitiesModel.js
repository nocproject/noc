//---------------------------------------------------------------------
// sa.service CapabilitiesModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.service.CapabilitiesModel");

Ext.define("NOC.sa.service.CapabilitiesModel", {
    extend: "Ext.data.Model",
    rest_url: "/sa/service/{{parent}}/caps/",
    parentField: "service_id",

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
