//---------------------------------------------------------------------
// sa.managedobject Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.Model");

Ext.define("NOC.sa.managedobject.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/managedobject/",

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
            name: "is_managed",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "administrative_domain",
            type: "int"
        },
        {
            name: "administrative_domain__label",
            type: "string",
            persist: false
        },
        {
            name: "auth_profile",
            type: "int"
        },
        {
            name: "auth_profile__label",
            type: "string",
            persist: false
        },
        {
            name: "activator",
            type: "int"
        },
        {
            name: "activator__label",
            type: "string",
            persist: false
        },
        {
            name: "collector",
            type: "int"
        },
        {
            name: "collector__label",
            type: "string",
            persist: false
        },
        {
            name: "profile_name",
            type: "string"
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
            name: "description",
            type: "string"
        },
        {
            name: "scheme",
            type: "int"
        },
        {
            name: "address",
            type: "string"
        },
        {
            name: "port",
            type: "int"
        },
        {
            name: "user",
            type: "string"
        },
        {
            name: "password",
            type: "string"
        },
        {
            name: "super_password",
            type: "string"
        },
        {
            name: "remote_path",
            type: "string"
        },
        {
            name: "trap_source_ip",
            type: "string"
        },
        {
            name: "trap_community",
            type: "string"
        },
        {
            name: "snmp_ro",
            type: "string"
        },
        {
            name: "snmp_rw",
            type: "string"
        },
        {
            name: "vc_domain",
            type: "int"
        },
        {
            name: "vc_domain__label",
            type: "string",
            persist: false
        },
        {
            name: "termination_group",
            type: "int"
        },
        {
            name: "termination_group__label",
            type: "string",
            persist: false
        },
        {
            name: "service_terminator",
            type: "int"
        },
        {
            name: "service_terminator__label",
            type: "string",
            persist: false
        },
        {
            name: "vrf",
            type: "int"
        },
        {
            name: "vrf__label",
            type: "string",
            persist: false
        },
        {
            name: "shape",
            type: "string"
        },
        {
            name: "config_filter_rule",
            type: "int"
        },
        {
            name: "config_filter_rule__label",
            type: "string",
            persist: false
        },
        {
            name: "config_diff_filter_rule",
            type: "int"
        },
        {
            name: "config_diff_filter_rule__label",
            type: "string",
            persist: false
        },
        {
            name: "config_validation_rule",
            type: "int"
        },
        {
            name: "config_validation_rule__label",
            type: "string",
            persist: false
        },
        {
            name: "max_scripts",
            type: "int"
        },
        {
            name: "tags",
            type: "auto"
        },
        {
            name: "platform",
            type: "string",
            persist: false
        },
        {
            name: "interface_count",
            type: "integer",
            persist: false
        },
        {
            name: "link_count",
            type: "integer",
            persist: false
        },
        {
            name: "row_class",
            type: "string",
            persist: false
        }
    ]
});
