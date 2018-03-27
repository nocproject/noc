//---------------------------------------------------------------------
// main.handler Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.handler.Model");

Ext.define("NOC.main.handler.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/handler/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "handler",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "allow_config_filter",
            type: "boolean"
        },
        {
            name: "allow_config_validation",
            type: "boolean"
        }
    ]
});
