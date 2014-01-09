//---------------------------------------------------------------------
// inv.inv RackLoadModel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.file.FileModel");

Ext.define("NOC.inv.inv.plugins.file.FileModel", {
    extend: "Ext.data.Model",
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
            name: "mime_type",
            type: "string"
        },
        {
            name: "size",
            type: "int"
        },
        {
            name: "ts",
            type: "date"
        },
        {
            name: "description",
            type: "string"
        }
    ]
});
