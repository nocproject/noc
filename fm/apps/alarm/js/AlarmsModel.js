//---------------------------------------------------------------------
// fm.alarm AlarmsModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.AlarmsModel");

Ext.define("NOC.fm.alarm.AlarmsModel", {
    extend: "Ext.data.Model",
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
            name: "subject",
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
            name: "row_class",
            type: "string"
        }
    ]
});
