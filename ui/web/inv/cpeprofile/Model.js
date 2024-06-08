//---------------------------------------------------------------------
// inv.cpeprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.cpeprofile.Model");

Ext.define("NOC.inv.cpeprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/inv/cpeprofile/",

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
            name: "shape",
            type: "string"
        },
        {
            name: "shape_title_template",
            type: "string"
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
            name: "pool",
            type: "string"
        },
        {
            name: "pool__label",
            type: "string",
            persist: false
        },
        {
            name: "object_profile",
            type: "int"
        },
        {
            name: "object_profile__label",
            type: "string",
            persist: false
        },
        {
            name: "sync_asset",
            type: "bool",
            defaultValue: false
        },
        {
            name: "sync_managedobject",
            type: "bool",
            defaultValue: false
        },
        {
            name: "cpe_status_discovery",
            type: "string",
            defaultValue: "D"
        },
        {
            name: "enable_collect",
            type: "bool",
            defaultValue: false
        },
        {
            name: "metrics_default_interval",
            type: "int",
            defaultValue: 1
        },
        {
            name: "metrics_interval_buckets",
            type: "int"
        },
        {
            name: "metrics",
            type: "auto"
        },
        {
            name: "bi_id",
            type: "string",
            persist: false
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
        }
    ]
});