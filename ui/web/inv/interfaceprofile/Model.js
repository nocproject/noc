//---------------------------------------------------------------------
// inv.interfaceprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2021 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.interfaceprofile.Model");

Ext.define("NOC.inv.interfaceprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/interfaceprofile/",

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
            name: "name",
            type: "string"
        },
        {
            name: "style",
            type: "int"
        },
        {
            name: "workflow",
            type: "string"
        },
        {
            name: "workflow__label",
            type: "string",
            persist: false
        },
        {
            name: "link_events",
            type: "string",
            defaultValue: "A"
        },
        {
            name: "mac_discovery_policy",
            type: "string",
            defaultValue: "e"
        },
        {
            name: "status_discovery",
            type: "string",
            defaultValue: "d"
        },
        {
            name: "metric_collected_policy",
            type: "string",
            defaultValue: "e"
        },
        {
            name: "metrics_default_interval",
            type: "int"
        },
        {
            name: "allow_lag_mismatch",
            type: "bool",
            defaultValue: false
        },
        {
            name: "weight",
            type: "int",
            defaultValue: 0
        },
        {
            name: "discovery_policy",
            type: "string",
            defaultValue: "R"
        },
        {
            name: "status_change_notification",
            type: "string"
        },
        {
            name: "default_notification_group",
            type: "string"
        },
        {
            name: "default_notification_group__label",
            type: "string",
            persist: false
        },
        {
            name: "metrics",
            type: "auto"
        },
        {
            name: "is_uni",
            type: "bool",
            defaultValue: false
        },
        {
            name: "remote_system",
            type: "string"
        },
        {
            name: "remote_system__label",
            type: "string",
            persist: false
        },
        {
            name: "remote_id",
            type: "string"
        },
        {
            name: "bi_id",
            type: "string",
            persist: false
        },
        {
            name: "allow_autosegmentation",
            type: "boolean"
        },
        {
            name: "allow_subinterface_metrics",
            type: "boolean"
        },
        {
            name: "interface_validation_policy",
            type: "string"
        },
        {
            name: "interface_validation_policy__label",
            type: "string",
            persist: false
        },
        {
            name: "ifdesc_patterns",
            type: "string"
        },
        {
            name: "ifdesc_patterns__label",
            type: "string",
            persist: false
        },
        {
            name: "ifdesc_handler",
            type: "string"
        },
        {
            name: "ifdesc_handler__label",
            type: "string",
            persist: false
        },
        {
            name: "allow_vacuum_bulling",
            type: "bool"
        },
        {
            name: "enable_abduct_detection",
            type: "bool"
        },
        {
            name: "labels",
            type: "auto"
        },
        {
            name: "dynamic_classification_policy",
            type: "string",
            defaultValue: "R"
        },
        // CSS
        {
            name: "row_class",
            type: "string",
            persist: false
        },
        // Foreign keys
        {
            name: "style__label",
            type: "string",
            persist: false
        },
        {
            name: "match_rules",
            type: "auto"
        },
        {
            name: "match_expression",
            type: "auto",
            persist: false
        },
    ]
});
