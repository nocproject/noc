//---------------------------------------------------------------------
// main.pool Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.pool.Model");

Ext.define("NOC.main.pool.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/pool/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        }
    ]
});
