//---------------------------------------------------------------------
// fm.alarmrule Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmrule.Model");

Ext.define("NOC.fm.alarmrule.Model", {
    extend: "Ext.data.Model",
    rest_url: "/fm/alarmrule/",

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
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "match",
            type: "auto"
        },
        {
            name: "groups",
            type: "auto"
        },
        {
            name: "actions",
            type: "auto"
        },
        {
            name: "severity_policy",
            type: "string",
            defaultValue: "AL"
        },
        {
            name: "escalation_profile",
            type: "string"
        },
        {
            name: "escalation_profile__label",
            type: "string",
            persist: false
        },
        {
            name: "stop_processing",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "bi_id",
            type: "string",
            persist: false
        },
    ]
});
