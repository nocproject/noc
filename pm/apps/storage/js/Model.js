//---------------------------------------------------------------------
// pm.storage Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
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
            name: "name",
            type: "string"
        },
        {
            name: "collectors",
            type: "auto"
        },
        {
            name: "access",
            type: "auto"
        },
        {
            name: "select_policy",
            type: "string"
        },
        {
            name: "write_concern",
            type: "integer"
        },
        {
            name: "type",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        }
    ]
});
