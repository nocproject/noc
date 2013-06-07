//---------------------------------------------------------------------
// pm.storage Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.storage.Model");

Ext.define("NOC.pm.storage.Model", {
    extend: "Ext.data.Model",
    rest_url: "/pm/storage/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "raw_retention",
            type: "int"
        },
        {
            name: "db",
            type: "string"
        },
        {
            name: "db__label",
            type: "string",
            persist: false
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "collection",
            type: "string"
        }
    ]
});
