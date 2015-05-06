//---------------------------------------------------------------------
// main.pendingnotifications Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.pendingnotifications.Model");

Ext.define("NOC.main.pendingnotifications.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/pendingnotifications/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "timestamp",
            type: "date"
        },
        {
            name: "notification_method",
            type: "string"
        },
        {
            name: "notification_params",
            type: "string"
        },
        {
            name: "subject",
            type: "string"
        },
        {
            name: "body",
            type: "string"
        },
        {
            name: "link",
            type: "string"
        },
        {
            name: "next_try",
            type: "date"
        },
        {
            name: "actual_till",
            type: "date"
        },
        {
            name: "tag",
            type: "string"
        }
    ]
});
