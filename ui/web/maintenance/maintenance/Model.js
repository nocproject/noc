//---------------------------------------------------------------------
// maintenance.maintenance Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.maintenance.maintenance.Model");

Ext.define("NOC.maintenance.maintenance.Model", {
    extend: "Ext.data.Model",
    rest_url: "/maintenance/maintenance/",

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
            name: "escalate_managed_object",
            type: "string"
        },
        {
            name: "escalate_managed_object__label",
            type: "string",
            persist: false
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
        },
        {
            name: "time_pattern",
            type: "string"
        },
        {
            name: "time_pattern__label",
            type: "string",
            persist: true
        }
    ]
});
