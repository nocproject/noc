//---------------------------------------------------------------------
// inv.coverage ObjectModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.coverage.ObjectModel");

Ext.define("NOC.inv.coverage.ObjectModel", {
    extend: "Ext.data.Model",
    rest_url: "/inv/coverage/{{parent}}/objects/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "preference",
            type: "integer"
        },
        {
            name: "object",
            type: "string"
        },
        {
            name: "object__label",
            type: "string",
            persist: false
        }
    ]
});
