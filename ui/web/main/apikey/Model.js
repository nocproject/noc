//---------------------------------------------------------------------
// main.apikey Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.apikey.Model");

Ext.define("NOC.main.apikey.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/apikey/",

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
            name: "expires",
            type: "auto"
        },
        {
            name: "is_active",
            type: "boolean"
        },
        {
            name: "access",
            type: "auto"
        },
        {
            name: "key",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        }
    ]
});
