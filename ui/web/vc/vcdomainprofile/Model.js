//---------------------------------------------------------------------
// vc.vcdomainprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vcdomainprofile.Model");

Ext.define("NOC.vc.vcdomainprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/vc/vcdomainprofile/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "style",
            type: "int"
        },
        {
            name: "style__label",
            type: "string",
            persist: false
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
            name: "description",
            type: "string"
        },
        {
            name: "bi_id",
            type: "int",
            persist: false
        },
        {
            name: "remote_id",
            type: "string"
        },
        {
            name: "default_vc_workflow",
            type: "string"
        },
        {
            name: "default_vc_workflow__label",
            type: "string",
            persist: false
        },
        {
            name: "vlan_provisioning_filter",
            type: "int"
        },
        {
            name: "enable_vlan_discovery",
            type: "boolean"
        },
        {
            name: "type",
            type: "string"
        },
        {
            name: "enable_vlan_provisioning",
            type: "boolean"
        },
        {
            name: "name",
            type: "string"
        }
    ]
});
