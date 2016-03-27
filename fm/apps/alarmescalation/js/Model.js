//---------------------------------------------------------------------
// fm.alarmescalation Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmescalation.Model");

Ext.define("NOC.fm.alarmescalation.Model", {
    extend: "Ext.data.Model",
    rest_url: "/fm/alarmescalation/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "alarm_classes",
            type: "auto"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "escalations",
            type: "auto"
        }
    ]
});
