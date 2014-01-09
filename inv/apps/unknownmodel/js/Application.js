//---------------------------------------------------------------------
// inv.unknownmodel application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.unknownmodel.Application");

Ext.define("NOC.inv.unknownmodel.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.inv.unknownmodel.Model"
    ],
    model: "NOC.inv.unknownmodel.Model",
    search: true,
    columns: [
        {
            text: "Vendor",
            dataIndex: "vendor",
            width: 70
        },
        {
            text: "Object",
            dataIndex: "managed_object",
            width: 100
        },
        {
            text: "Part No",
            dataIndex: "part_no",
            width: 100
        },
        {
            text: "Description",
            dataIndex: "description",
            flex: 1
        }
    ],
    fields: [
    ]
});
