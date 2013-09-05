//---------------------------------------------------------------------
// main.customfieldenumgroup Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.customfieldenumgroup.Model");

Ext.define("NOC.main.customfieldenumgroup.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/customfieldenumgroup/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "description",
            type: "string"
        }
    ]
});
