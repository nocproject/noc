//---------------------------------------------------------------------
// main.audittrail Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.audittrail.Model");

Ext.define("NOC.main.audittrail.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/audittrail/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "user",
            type: "string"
        },
        {
            name: "timestamp",
            type: "string"
        },
        {
            name: "model_id",
            type: "string"
        },
        {
            name: "op",
            type: "string"
        },
        {
            name: "changes",
            type: "auto"
        }
    ]
});
