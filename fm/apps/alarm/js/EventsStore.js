//---------------------------------------------------------------------
// fm.alarm EventsStore
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.EventsStore");

Ext.define("NOC.fm.alarm.EventsStore", {
    extend: "Ext.data.Store",
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
            type: "string"
        }
    ],
    data: []
});
