//---------------------------------------------------------------------
// fm.escalationprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.escalationprofile.Model");

Ext.define("NOC.fm.escalationprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/fm/escalationprofile/",

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
            name: "description",
            type: "string"
        },
        {
            name: "escalation_policy",
            type: "integer",
            defaultValue: 2
        },
        {
            name: "maintenance_policy",
            type: "string",
            defaultValue: "i"
        },
        {
            name: "alarm_consequence_policy",
            type: "string",
            defaultValue: "a"
        },
        {
            name: "end_condition",
            type: "string",
            defaultValue: "CR"
        },
        {
            name: "close_alarm",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "escalations",
            type: "auto"
        },
        {
            name: "tt_system",
            type: "auto"
        },
        {
            name: "telemetry_sample",
            type: "integer",
            defaultValue: 0
        }
    ]
});
