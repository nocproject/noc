//---------------------------------------------------------------------
// main.notificationgroupusersubscription Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.notificationgroupusersubscription.Model");

Ext.define("NOC.main.notificationgroupusersubscription.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/notificationgroupusersubscription/",

    fields: [
        {
            name: "id",
            type: "int"
        },
        {
            name: "notification_group",
            type: "int"
        },
        {
            name: "notification_group__label",
            type: "string",
            persist: false
        },
        {
            name: "time_pattern",
            type: "int"
        },
        {
            name: "time_pattern__label",
            type: "string",
            persist: false
        },
        {
            name: "user",
            type: "int"
        },
        {
            name: "user__label",
            type: "string",
            persist: false
        },
        {
            name: "expired_at",
            type: "string"
        },
        {
            name: "suppress",
            type: "boolean"
        },
        {
            name: "remote_system",
            type: "string"
        },
        {
            name: "watch",
            type: "string",
            persist: false
        },
        {
            name: "remote_system__label",
            type: "string",
            persist: false
        }
    ]
});
