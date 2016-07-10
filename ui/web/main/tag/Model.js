//---------------------------------------------------------------------
// main.tag Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.tag.Model");

Ext.define("NOC.main.tag.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/tag/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        }
    ]
});
