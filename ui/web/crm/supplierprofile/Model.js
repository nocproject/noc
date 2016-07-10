//---------------------------------------------------------------------
// crm.supplierprofile Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.crm.supplierprofile.Model");

Ext.define("NOC.crm.supplierprofile.Model", {
    extend: "Ext.data.Model",
    rest_url: "/crm/supplierprofile/",

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
            name: "description",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "tags",
            type: "auto"
        },
        {
            name: "row_class",
            type: "string",
            persist: false
        }
    ]
});
