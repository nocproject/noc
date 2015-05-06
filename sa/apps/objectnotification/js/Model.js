//---------------------------------------------------------------------
// sa.objectnotification Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.objectnotification.Model");

Ext.define("NOC.sa.objectnotification.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/objectnotification/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "selector",
            type: "int"
        },
        {
            name: "selector__label",
            type: "string",
            persist: false
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
            name: "config_changed",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "alarm_risen",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "alarm_reopened",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "alarm_cleared",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "alarm_commented",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "new",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "deleted",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "version_changed",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "interface_changed",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "script_failed",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "config_policy_violation",
            type: "boolean",
            defaultValue: false
        }
    ]
});
