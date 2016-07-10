//---------------------------------------------------------------------
// vc.vctype Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.vc.vctype.Model");

Ext.define("NOC.vc.vctype.Model", {
    extend: "Ext.data.Model",
    rest_url: "/vc/vctype/",

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
            name: "min_labels",
            type: "int"
        },

        {
            name: "label1_min",
            type: "int"
        },

        {
            name: "label1_max",
            type: "int"
        },

        {
            name: "label2_min",
            type: "int"
        },

        {
            name: "label2_max",
            type: "int"
        },
        // Calculated fields
        {
            name: "l1",
            type: "string",
            persist: false,
            convert: function(value, record) {
                var l1_min = record.get("label1_min"),
                    l1_max = record.get("label1_max");
                return l1_min.toString() + "-" + l1_max.toString();
            }
        },

        {
            name: "l2",
            type: "string",
            persist: false,
            convert: function(value, record) {
                var l2_min = record.get("label2_min"),
                    l2_max = record.get("label2_max");
                if(!l2_min && !l2_max)
                    return "";
                else
                    return l2_min.toString() + "-" + l2_max.toString();
            }
        }

    ]
});
