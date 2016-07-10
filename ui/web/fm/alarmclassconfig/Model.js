//---------------------------------------------------------------------
// fm.alarmclassconfig Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmclassconfig.Model");

Ext.define("NOC.fm.alarmclassconfig.Model", {
    extend: "Ext.data.Model",
    rest_url: "/fm/alarmclassconfig/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "alarm_class",
            type: "string"
        },
        {
            name: "alarm_class__label",
            type: "string",
            persist: false
        },
        {
            name: "control_time0",
            type: "int"
        },
        {
            name: "control_time1",
            type: "int"
        },
        {
            name: "control_timeN",
            type: "int"
        },
        {
            name: "notification_delay",
            type: "int"
        }
    ]
});
