//---------------------------------------------------------------------
// vc.vpnprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vpnprofile.Model");

Ext.define("NOC.vc.vpnprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/vc/vpnprofile/",

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
            name: "remote_id",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "type",
            type: "string",
            defaultValue: "vrf"
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
            name: "bi_id",
            type: "string",
            persist: false
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "tags",
            type: "auto"
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
            name: "default_prefix_profile",
            type: "string"
        },
        {
            name: "default_prefix_profile__label",
            type: "string",
            persist: false
        }
    ]
});
