//---------------------------------------------------------------------
// fm.alarmclass Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmclass.Model");

Ext.define("NOC.fm.alarmclass.Model", {
    extend: "Ext.data.Model",
    rest_url: "/fm/alarmclass/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "category",
            type: "string"
        },
        {
            name: "flap_threshold",
            type: "float"
        },
        {
            name: "jobs",
            type: "auto",
        },
        {
            name: "datasources",
            type: "auto",
        },
        {
            name: "components",
            type: "auto",
        },
        {
            name: "vars",
            type: "auto",
        },
        {
            name: "flap_condition",
            type: "string"
        },
        {
            name: "subject_template",
            type: "string"
        },
        {
            name: "body_template",
            type: "string"
        },
        {
            name: "symptoms",
            type: "string"
        },
        {
            name: "probable_causes",
            type: "string"
        },
        {
            name: "recommended_actions",
            type: "string"
        },
        {
            name: "root_cause",
            type: "auto"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "flap_window",
            type: "int"
        },
        {
            name: "reference",
            type: "auto",
        },
        {
            name: "is_builtin",
            type: "boolean",
            persist: false
        },
        {
            name: "uuid",
            type: "string",
            persist: false
        },
        {
            name: "is_unique",
            type: "boolean"
        },
        {
            name: "is_ephemeral",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "user_clearable",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "by_reference",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "handlers"
        },
        {
            name: "clear_handlers"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "recover_time",
            type: "int"
        },
        {
            name: "labels",
            type: "auto"
        },
        {
            name: "row_class",
            type: "string",
            persist: false
        }
    ]
});
