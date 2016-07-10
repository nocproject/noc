//---------------------------------------------------------------------
// vc.vcbindfilter Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vcbindfilter.Model");

Ext.define("NOC.vc.vcbindfilter.Model", {
    extend: "Ext.data.Model",
    rest_url: "/vc/vcbindfilter/",

    fields: [
        {
            name: "id",
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
            name: "vrf",
            type: "int"
        },
        {
            name: "vrf__label",
            type: "string",
            persist: false
        },
        {
            name: "afi",
            type: "string",
            defaultValue: "4"
        },
        {
            name: "prefix",
            type: "string"
        },
        {
            name: "vc_filter",
            type: "int"
        },
        {
            name: "vc_filter__label",
            type: "string",
            persist: false
        },
        {
            name: "vc_filter_expression",
            type: "string",
            persist: false
        }
    ]
});
