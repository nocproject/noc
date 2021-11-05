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
            match: "rules",
            type: "auto"
        },
        {
            match: "groups",
            type: "auto"
        },
        {
            match: "actions",
            type: "auto"
        },
        {
            name: "bi_id",
            type: "string",
            persist: false
        },
    ]
});
