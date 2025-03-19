//---------------------------------------------------------------------
// fm.dispositionrule Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.dispositionrule.Model");

Ext.define("NOC.fm.dispositionrule.Model", {
    extend: "Ext.data.Model",
    rest_url: "/fm/dispositionrule/",

    fields: [
        {
            name: "id",
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
            name: "uuid",
            type: "string"
        },
        {
            name: "is_builtin",
            type: "boolean",
            persist: false
        },
        {
            name: "match",
            type: "auto"
        },
        {
            name: "combo_condition",
            type: "string"
        },
        {
            name: "combo_window",
            type: "int",
            defaultValue: 0
        },
        {
            name: "combo_count",
            type: "int",
            defaultValue: 0
        },
        {
            name: "replace_rule_policy",
            type: "string"
        },
        {
            name: "replace_rule",
            type: "string"
        },
        {
            name: "replace_rule__label",
            type: "string",
            persist: false
        },
        {
            name: "notification_group",
            type: "string"
        },
        {
            name: "notification_group__label",
            type: "string",
            persist: false
        },
        {
            name: "subject_template",
            type: "string"
        },
        {
            name: "severity_policy",
            type: "string"
        },
        {
            name: "object_actions",
            type: "auto"
        },
        {
            name: "root_cause",
            type: "auto"
        },
        {
            name: "preference",
            type: "int",
            defaultValue: 1000
        },
        {
            name: "stop_processing",
            type: "boolean"
        },
        {
            name: "alarm_disposition",
            type: "string"
        },
        {
            name: "alarm_disposition__label",
            type: "string",
            persist: false
        },
        {
            name: "bi_id",
            type: "string",
            persist: false
        }
    ]
});
