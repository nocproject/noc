//---------------------------------------------------------------------
// vc.vlanprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2017 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vlanprofile.Model");

Ext.define("NOC.vc.vlanprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/vc/vlanprofile/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "enable_provisioning",
            type: "boolean"
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
            name: "role",
            type: "string"
        },
        {
            name: "labels",
            type: "auto"
        },
        {
            name: "remote_id",
            type: "string"
        },
        {
            name: "workflow",
            type: "string"
        },
        {
            name: "bi_id",
            type: "int"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "row_class",
            type: "string",
            persist: false
        }
    ]
});
