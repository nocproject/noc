//---------------------------------------------------------------------
// fm.ttsystem Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.ttsystem.Model");

Ext.define("NOC.fm.ttsystem.Model", {
    extend: "Ext.data.Model",
    rest_url: "/fm/ttsystem/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "connection",
            type: "string"
        },
        {
            name: "login",
            type: "string"
        },
        {
            name: "handler",
            type: "string"
        },
        {
            name: "update_handler",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "failure_cooldown",
            type: "int"
        },
        {
            name: "is_active",
            type: "boolean"
        },
        {
            name: "max_threads",
            type: "int"
        },
        {
            name: "shard_name",
            type: "string"
        },
        {
            name: "telemetry_sample",
            type: "int"
        },
        {
            name: "alarm_consequence_policy",
            type: "string"
        },
        {
            name: "promote_items",
            type: "string",
            defaultValue: "T",
        }
    ]
});
