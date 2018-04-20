//---------------------------------------------------------------------
// fm.alarmclass Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
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
            name: "default_severity",
            type: "string"
        },
        {
            name: "discriminator",
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
            name: "user_clearable",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "row_class",
            type: "string",
            persist: false
        }
    ]
});
