//---------------------------------------------------------------------
// inv.coverage Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.coverage.Model");

Ext.define("NOC.inv.coverage.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/coverage/",

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
            name: "description",
            type: "string"
        }
    ]
});
