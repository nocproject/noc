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
            type: "auto"            
        },
        {
            name: "filter_profile",
            type: "string"
        },
        {
            name: "filter_profile__label",
            type: "string",
            persist: false
        },
        {
            name: "filter_vendor",
            type: "string"
        },
        {
            name: "filter_vendor__label",
            type: "string",
            persist: false
        },
        {
            name: "filter_platform",
            type: "string"
        },
        {
            name: "filter_platform__label",
            type: "string",
            persist: false
        },
        {
            name: "filter_version",
            type: "string"
        },
        {
            name: "filter_version__label",
            type: "string",
            persist: false
        },
        {
            name: "filter_pool",
            type: "string"
        },
        {
            name: "filter_pool__label",
            type: "string",
            persist: false
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
            name: "filter_administrative_domain",
            type: "int"
        },
        {
            name: "filter_administrative_domain__label",
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
            name: "filter_service_group",
            type: "string"
        },
        {
            name: "filter_service_group__label",
            type: "string",
            persist: false
        },
        {
            name: "filter_client_group",
            type: "string"
        },
        {
            name: "filter_client_group__label",
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
            name: "filter_tt_system",
            type: "string"
        },
        {
            name: "filter_tt_system__label",
            type: "string",
            persist: false
        },
        {
            name: "filter_labels",
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
