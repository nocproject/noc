//---------------------------------------------------------------------
// maintainance.maintainance Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.maintainance.maintainance.Model");

Ext.define("NOC.maintainance.maintainance.Model", {
    extend: "Ext.data.Model",
    rest_url: "/maintainance/maintainance/",

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
            name: "contacts",
            type: "string"
        },
        {
            name: "type",
            type: "string"
        },
        {
            name: "type__label",
            type: "string"
        },
        {
            name: "stop",
            type: "auto"
        },
        {
            name: "start",
            type: "auto"
        },
        {
            name: "suppress_alarms",
            type: "boolean"
        },
        {
            name: "is_completed",
            type: "boolean"
        },
        {
            name: "direct_objects",
            type: "auto"
        },
        {
            name: "direct_segments",
            type: "auto"
        },
        {
            name: "subject",
            type: "string"
        }
    ]
});
