//---------------------------------------------------------------------
// sa.managedobjectselector Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobjectselector.Model");

Ext.define("NOC.sa.managedobjectselector.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/managedobjectselector/",

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
            name: "is_enabled",
            type: "boolean"
        },
        {
            name: "filter_id",
            type: "int"
        },
        {
            name: "filter_name",
            type: "string"
        },
        {
            name: "filter_managed",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "filter_profile",
            type: "string"
        },
        {
            name: "filter_object_profile",
            type: "int"
        },
        {
            name: "filter_object_profile__label",
            type: "string",
            persist: false
        },
        {
            name: "filter_address",
            type: "string"
        },
        {
            name: "filter_prefix",
            type: "int"
        },
        {
            name: "filter_prefix__label",
            type: "string",
            persist: false
        },
        {
            name: "filter_shard",
            type: "int"
        },
        {
            name: "filter_shard__label",
            type: "string",
            persist: false
        },
        {
            name: "filter_administrative_domain",
            type: "int"
        },
        {
            name: "filter_administrative_domain__label",
            type: "string",
            persist: false
        },
        {
            name: "filter_activator",
            type: "int"
        },
        {
            name: "filter_activator__label",
            type: "string",
            persist: false
        },
        {
            name: "filter_vrf",
            type: "int"
        },
        {
            name: "filter_vrf__label",
            type: "string",
            persist: false
        },
        {
            name: "filter_vc_domain",
            type: "int"
        },
        {
            name: "filter_vc_domain__label",
            type: "string",
            persist: false
        },
        {
            name: "filter_termination_group",
            type: "int"
        },
        {
            name: "filter_termination_group__label",
            type: "string",
            persist: false
        },
        {
            name: "filter_service_terminator",
            type: "int"
        },
        {
            name: "filter_service_terminator__label",
            type: "string",
            persist: false
        },
        {
            name: "filter_user",
            type: "string"
        },
        {
            name: "filter_remote_path",
            type: "string"
        },
        {
            name: "filter_description",
            type: "string"
        },
        {
            name: "filter_repo_path",
            type: "string"
        },
        {
            name: "filter_tags",
            type: "auto"
        },
        {
            name: "source_combine_method",
            type: "string",
            defaultValue: "O"
        },
        {
            name: "sources",
            type: "auto"
        },
        {
            name: "expression",
            type: "string",
            persist: false
        }
    ]
});
