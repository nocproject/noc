//---------------------------------------------------------------------
// fm.alarm Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.Model");

Ext.define("NOC.fm.alarm.Model", {
    extend: "Ext.data.Model",
    rest_url: "/fm/alarm/",
    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "status",
            type: "string"
        },
        {
            name: "managed_object",
            type: "int"
        },
        {
            name: "managed_object__label",
            type: "string"
        },
        {
            name: "alarm_class",
            type: "string"
        },
        {
            name: "alarm_class__label",
            type: "string"
        },
        {
            name: "timestamp",
            type: "date"
        },
        {
            name: "clear_timestamp",
            type: "date"
        },
        {
            name: "subject",
            type: "string"
        },
        {
            name: "events",
            type: "int"
        },
        {
            name: "row_class",
            type: "string",
            persist: true
        },
        {
            name: "duration",
            type: "int"
        },
        {
            name: "severity",
            type: "int"
        },
        {
            name: "severity__label",
            type: "string"
        },
        {
            name: "segment",
            type: "auto"
        },
        {
            name: "location",
            type: "auto"
        },
        {
            name: "segment__label",
            type: "auto",
            persist: true
        }
    ]
});
