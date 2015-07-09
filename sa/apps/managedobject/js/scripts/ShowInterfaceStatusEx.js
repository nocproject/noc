//---------------------------------------------------------------------
// ShowInterfaceStatus
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.scripts.ShowInterfaceStatusEx");

Ext.define("NOC.sa.managedobject.scripts.ShowInterfaceStatusEx", {
    extend: "NOC.sa.managedobject.scripts.TablePreview",
    columns: [
        {
            text: "Interface",
            dataIndex: "interface",
            width: 120,
        },
        {
            text: "Oper",
            dataIndex: "oper_status",
            renderer: NOC.render.Bool,
            width: 50
        },
        {
            text: "Admin",
            dataIndex: "admin_status",
            renderer: NOC.render.Bool,
            width: 50
        },
        {
            text: "In (kbit/s)",
            dataIndex: "in_speed",
            width: 70,
            align: "right"
        },
        {
            text: "Out (kbit/s)",
            dataIndex: "out_speed",
            width: 70,
            align: "right"
        },
        {
            text: "Full Duplex",
            dataIndex: "full_duplex",
            width: 70,
            renderer: NOC.render.Bool
        }
    ],
    search: true
});
