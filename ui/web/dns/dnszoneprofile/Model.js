//---------------------------------------------------------------------
// dns.dnszoneprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.dns.dnszoneprofile.Model");

Ext.define("NOC.dns.dnszoneprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/dns/dnszoneprofile/",

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
            name: "masters",
            type: "auto"
        },
        {
            name: "masterslabel",
            type: "auto",
            persist: false
        },
        {
            name: "slaves",
            type: "auto"
        },
        {
            name: "slaveslabel",
            type: "auto",
            persist: false
        },
        {
            name: "zone_soa",
            type: "string"
        },
        {
            name: "zone_contact",
            type: "string"
        },
        {
            name: "zone_refresh",
            type: "int",
            defaultValue: 3600
        },
        {
            name: "zone_retry",
            type: "int",
            defaultValue: 900
        },
        {
            name: "zone_expire",
            type: "int",
            defaultValue: 86400
        },
        {
            name: "zone_ttl",
            type: "int",
            defaultValue: 3600
        },
        {
            name: "notification_group",
            type: "int"
        },
        {
            name: "notification_group__label",
            type: "string",
            persist: false
        },
        {
            name: "description",
            type: "string"
        }
    ]
});
