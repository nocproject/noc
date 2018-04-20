//---------------------------------------------------------------------
// vc.vc Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vc.Model");

Ext.define("NOC.vc.vc.Model", {
    extend: "Ext.data.Model",
    rest_url: "/vc/vc/",

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
            name: "name",
            type: "string"
        },
        {
            name: "l1",
            type: "int"
        },
        {
            name: "l2",
            type: "int"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "style",
            type: "int"
        },
        {
            name: "tags",
            type: "auto"
        },
        // Foreign keys
        {
            name: "vc_domain__label",
            type: "string",
            persist: false
        },
        {
            name: "style__label",
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
            name: "project",
            type: "int"
        },
        {
            name: "project__label",
            type: "string",
            persist: false
        },
        // Info fields
        {
            name: "interfaces_count",
            type: "auto",
            persist: false
        },
        {
            name: "prefixes",
            type: "auto",
            persist: false
        },
        {
            name: "row_class",
            type: "string",
            persist: false
        },
        {
            name: "label",
            type: "string",
            persist: false,
            convert: function(value, record) {
                var l1 = record.get("l1"),
                    l2 = record.get("l2");
                if (l2)
                    return l1.toString() + ", " + l2.toString();
                else
                    return l1.toString();
            }
        }
    ]
});
