//---------------------------------------------------------------------
// pm.database Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.pm.database.Model");

Ext.define("NOC.pm.database.Model", {
    extend: "Ext.data.Model",
    rest_url: "/pm/database/",

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
            name: "database",
            type: "string"
        },
        {
            name: "host",
            type: "string"
        },
        {
            name: "user",
            type: "string"
        },
        {
            name: "password",
            type: "string"
        },
        {
            name: "port",
            type: "int"
        }
    ]
});
