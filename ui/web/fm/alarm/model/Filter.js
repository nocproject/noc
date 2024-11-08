//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.model.Filter");

Ext.define("NOC.fm.alarm.model.Filter", {
    extend: "Ext.data.Model",
    fields: [
        {
            name: "status",
            type: "string"
        },
        {
            name: "collapse",
            type: "int"
        },
        {
            name: "wait_tt",
            type: "int"
        },
        {
            name: "maintenance",
            type: "string"
        },
        {
            name: "alarm_group",
            type: "string"
        },
        {
            name: "ephemeral",
            type: "int"
        },
        {
            name: "managed_object",
            type: "int"
        },
        {
            name: "segment",
            type: "string"
        },
        {
            name: "administrative_domain",
            type: "int"
        },
        {
            name: "resource_group",
            type: "string"
        },
        {
            name: "alarm_class",
            type: "string"
        },
        {
            name: "escalation_tt__contains",
            type: "string"
        },
        {
            name: "timestamp__gte",
            type: "date"
        },
        {
            name: "timestamp__lte",
            type: "date"
        }
    ]
});