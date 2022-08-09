//---------------------------------------------------------------------
// sa.objectdiagnosticconfig Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.objectdiagnosticconfig.Model");

Ext.define("NOC.sa.objectdiagnosticconfig.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/objectdiagnosticconfig/",

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
            type: "boolean"
        },
        {
            name: "show_in_display",
            type: "boolean"
        },
        {
            name: "display_order",
            type: "int",
            defaultValue: 1000
        },
        {
            name: "state_policy",
            type: "string",
            defaultValue: "ANY"
        },
        {
            name: "checks",
            type: "auto"
        },
        {
            name: "diagnostics",
            type: "auto"
        },
        {
            name: "alarm_class",
            type: "string"
        },
        {
            name: "alarm_labels",
            type: "auto"
        },
        {
            name: "runs",
            type: "auto"
        },
        {
            name: "uuid",
            type: "string",
            persist: false
        },
        {
            name: "bi_id",
            type: "string",
            persist: false
        },
        {
            name: "is_builtin",
            type: "boolean",
            persist: false
        }
    ]
});
