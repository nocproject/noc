//---------------------------------------------------------------------
// fm.alarmgrouprule Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarmgrouprule.Model");

Ext.define("NOC.fm.alarmgrouprule.Model", {
    extend: "Ext.data.Model",
    rest_url: "/fm/alarmgrouprule/",

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
            name: "rules",
            type: "auto"
        },
        {
            name: "group_reference",
            type: "string"
        },
        {
            name: "group_alarm_class",
            type: "string"
        },
        {
            name: "group_alarm_class__label",
            type: "string",
            persist: false
        },
        {
            name: "group_title_template",
            type: "string"
        },
        {
            name: "handler",
            type: "string"
        },
        {
            name: "handler__label",
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
            name: "bi_id",
            type: "string",
            persist: false
        },
    ]
});
