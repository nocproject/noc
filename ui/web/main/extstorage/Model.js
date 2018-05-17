//---------------------------------------------------------------------
// main.extstorage Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.extstorage.Model");

Ext.define("NOC.main.extstorage.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/extstorage/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "url",
            type: "string"
        },
        {
            name: "enable_config_mirror",
            type: "boolean"
        },
        {
            name: "enable_beef",
            type: "boolean"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        }
    ]
});
