//---------------------------------------------------------------------
// fm.event Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.event.Model");

Ext.define("NOC.fm.event.Model", {
    extend: "Ext.data.Model",
    rest_url: "/fm/event/",
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
            name: "event_class",
            type: "string"
        },
        {
            name: "event_class__label",
            type: "string"
        },
        {
            name: "timestamp",
            type: "date"
        },
        {
            name: "subject",
            type: "str"
        },
        {
            name: "repeats",
            type: "int"
        },
        {
            name: "alarms",
            type: "int"
        },
        {
            name: "duration",
            type: "int"
        },
        {
            name: "row_class",
            type: "string"
        }
    ]
});
