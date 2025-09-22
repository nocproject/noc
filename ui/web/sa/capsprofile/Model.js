//---------------------------------------------------------------------
// sa.capsprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.capsprofile.Model");

Ext.define("NOC.sa.capsprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/sa/capsprofile/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "isis_policy",
            type: "string",
            defaultValue: "T"
        },
        {
            name: "lldp_policy",
            type: "string",
            defaultValue: "T"
        },
        {
            name: "bfd_policy",
            type: "string",
            defaultValue: "T"
        },
        {
            name: "ospf_policy",
            type: "string",
            defaultValue: "T"
        },
        {
            name: "hsrp_policy",
            type: "string",
            defaultValue: "T"
        },
        {
            name: "rsvp_policy",
            type: "string",
            defaultValue: "T"
        },
        {
            name: "udld_policy",
            type: "string",
            defaultValue: "T"
        },
        {
            name: "rep_policy",
            type: "string",
            defaultValue: "T"
        },
        {
            name: "ldp_policy",
            type: "string",
            defaultValue: "T"
        },
        {
            name: "oam_policy",
            type: "string",
            defaultValue: "T"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "huawei_ndp_policy",
            type: "string",
            defaultValue: "T"
        },
        {
            name: "cdp_policy",
            type: "string",
            defaultValue: "T"
        },
        {
            name: "vrrp_policy",
            type: "string",
            defaultValue: "T"
        },
        {
            name: "fdp_policy",
            type: "string",
            defaultValue: "T"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "bgp_policy",
            type: "string",
            defaultValue: "T"
        },
        {
            name: "stp_policy",
            type: "string",
            defaultValue: "T"
        },
        {
            name: "enable_l3",
            type: "boolean"
        },
        {
            name: "enable_l2",
            type: "boolean"
        },
        {
            name: "enable_snmp",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "enable_snmp_v1",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "enable_snmp_v2c",
            type: "boolean",
            defaultValue: true
        },
        {
            name: "vrrpv3_policy",
            type: "string",
            defaultValue: "T"
        },
        {
            name: "lacp_policy",
            type: "string",
            defaultValue: "T"
        },
        {
            name: "ospfv3_policy",
            type: "string",
            defaultValue: "T"
        },
        {
            name: "caps",
            type: "auto"
        }
    ]
});
