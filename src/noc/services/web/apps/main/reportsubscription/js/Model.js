//---------------------------------------------------------------------
// main.reportsubscription Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.reportsubscription.Model");

Ext.define("NOC.main.reportsubscription.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/reportsubscription/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "notification_group",
            type: "int"
        },
        {
            name: "run_as",
            type: "int"
        },
        {
            name: "file_name",
            type: "string"
        },
        {
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "last_run",
            type: "auto"
        },
        {
            name: "last_status",
            type: "boolean"
        },
        {
            name: "subject",
            type: "string"
        },
        {
            name: "report_id",
            type: "string"
        }
    ]
});
