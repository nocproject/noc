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
        }
    ]
});
