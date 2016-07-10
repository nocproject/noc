//---------------------------------------------------------------------
// fm.alarmtrigger Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmtrigger.Model");

Ext.define("NOC.fm.alarmtrigger.Model", {
    extend: "Ext.data.Model",
    rest_url: "/fm/alarmtrigger/",

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
            name: "is_enabled",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "alarm_class_re",
            type: "string"
        },
        {
            name: "condition",
            type: "string",
            defaultValue: "True"
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
            name: "template",
            type: "int"
        },
        {
            name: "template__label",
            type: "string",
            persist: false
        },
        {
            name: "pyrule",
            type: "int"
        },
        {
            name: "pyrule__label",
            type: "string",
            persist: false
        }
    ]
});
