//---------------------------------------------------------------------
// main.customfieldenumgroup Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.customfieldenumgroup.ValuesModel");

Ext.define("NOC.main.customfieldenumgroup.ValuesModel", {
    extend: "Ext.data.Model",
    rest_url: "/main/customfieldenumgroup/{{parent}}/values/",
    parentField: "enum_group_id",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "is_active",
            type: "boolean"
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
