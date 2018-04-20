//---------------------------------------------------------------------
// support.crashinfo Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.support.crashinfo.Model");

Ext.define("NOC.support.crashinfo.Model", {
    extend: "Ext.data.Model",
    rest_url: "/support/crashinfo/",
    idProperty: "uuid",

    fields: [
        {
            name: "status",
            type: "string",
            defaultValue: "N"
        },
        {
            name: "uuid",
            type: "string"
        },
        {
            name: "process",
            type: "string"
        },
        {
            name: "timestamp",
            type: "auto"
        },
        {
            name: "tip",
            type: "string"
        },
        {
            name: "branch",
            type: "string"
        },
        {
            name: "comment",
            type: "string"
        },
        {
            name: "priority",
            type: "string"
        }
    ]
});
