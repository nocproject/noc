//---------------------------------------------------------------------
// main.crontab Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.crontab.Model");

Ext.define("NOC.main.crontab.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/crontab/",

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
            name: "hours_expr",
            type: "string",
            defaultValue: "*"
        },
        {
            name: "seconds_expr",
            type: "string",
            defaultValue: "0"
        },
        {
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "days_expr",
            type: "string",
            defaultValue: "*"
        },
        {
            name: "years_expr",
            type: "string",
            defaultValue: "*"
        },
        {
            name: "handler",
            type: "string"
        },
        {
            name: "minutes_expr",
            type: "string",
            defaultValue: "*"
        },
        {
            name: "weekdays_expr",
            type: "string",
            defaultValue: "*"
        },
        {
            name: "months_expr",
            type: "string",
            defaultValue: "*"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "crontab_expression",
            type: "string",
            persist: false
        }
    ]
});
