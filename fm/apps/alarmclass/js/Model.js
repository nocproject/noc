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
        /*
        {
            name: "jobs",
            type: "auto",
            defaultValue: <function <lambda> at 0x103e448c0>
        },
        {
            name: "datasources",
            type: "auto",
            defaultValue: <function <lambda> at 0x103e446e0>
        },
        {
            name: "vars",
            type: "auto",
            defaultValue: <function <lambda> at 0x103e44758>
        },
        */
        {
            name: "flap_condition",
            type: "string"
        },
        /*
        {
            name: "text",
            type: "auto",
            defaultValue: <function <lambda> at 0x103e447d0>
        },
        {
            name: "root_cause",
            type: "auto",
            defaultValue: <function <lambda> at 0x103e44848>
        },*/
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
        /*
        {
            name: "discriminator",
            type: "auto",
            defaultValue: <function <lambda> at 0x103e44668>
        },
        */
        {
            name: "is_builtin",
            type: "boolean"
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
        }
    ]
});
