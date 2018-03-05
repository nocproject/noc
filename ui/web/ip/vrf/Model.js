//---------------------------------------------------------------------
// ip.vrf Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.vrf.Model");

Ext.define("NOC.ip.vrf.Model", {
    extend: "Ext.data.Model",
    rest_url: "/ip/vrf/",

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
            name: "vrf_group",
            type: "int"
        },
        {
            name: "vrf_group__label",
            type: "string",
            persist: false
        },
        {
            name: "rd",
            type: "string"
        },
        {
            name: "afi_ipv4",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "afi_ipv6",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "tt",
            type: "int"
        },
        {
            name: "tags",
            type: "auto"
        },
        {
            name: "profile",
            type: "string"
        },
        {
            name: "profile__label",
            type: "string",
            persist: false
        },
        {
            name: "project",
            type: "int"
        },
        {
            name: "project__label",
            type: "string",
            persist: false
        },
        {
            name: "state",
            type: "int"
        },
        {
            name: "state__label",
            type: "string",
            persist: false
        },
        {
            name: "allocated_till",
            type: "date"
        },
        {
            name: "row_class",
            type: "string",
            persist: false
        }
    ]
});
