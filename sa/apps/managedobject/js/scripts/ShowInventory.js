//---------------------------------------------------------------------
// ShowInventory
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.scripts.ShowInventory");

Ext.define("NOC.sa.managedobject.scripts.ShowInventory", {
    extend: "NOC.sa.managedobject.scripts.TablePreview",
    columns: [
        {
            text: "Type",
            dataIndex: "type",
            width: 90,
        },
        {
            text: "Number",
            dataIndex: "number",
            width: 50,
        },
        {
            text: "Builtin",
            dataIndex: "builtin",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Vendor",
            dataIndex: "vendor",
            width: 90,
        },
        {
            text: "Part No",
            dataIndex: "part_no",
            width: 230,
        },
        {
            text: "Revision",
            dataIndex: "revision",
            width: 70,
        },
        {
            text: "Serial No",
            dataIndex: "serial",
            width: 120,
        },
        {
            text: "Description",
            dataIndex: "description",
            flex: 1
        }
    ],
    search: true
});
