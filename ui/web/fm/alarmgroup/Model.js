//---------------------------------------------------------------------
// fm.alarmgroup Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmgroup.Model");

Ext.define("NOC.fm.alarmgroup.Model", {
    extend: "Ext.data.Model",
    rest_url: "/fm/alarmgroup/",

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
            name: "is_active",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "preference",
            type: "int",
            defaultValue: 999
        },
        {
            name: "reference_prefix",
            type: "string"
        },
        {
            name: "labels",
            type: "auto"
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
            name: "title_template",
            type: "string"
        },
        {
            name: "bi_id",
            type: "string",
            persist: false
        },
    ]
});
