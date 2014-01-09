//---------------------------------------------------------------------
// ShowMPLSVPN
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.scripts.ShowMPLSVPN");

Ext.define("NOC.sa.managedobject.scripts.ShowMPLSVPN", {
    extend: "NOC.sa.managedobject.scripts.TablePreview",
    columns: [
        {
            text: "Name",
            dataIndex: "name",
            width: 120
        },
        {
            text: "Status",
            dataIndex: "status",
            width: 50,
            renderer: NOC.render.Bool
        },
        {
            text: "Type",
            dataIndex: "type",
            width: 70
        },
        {
            text: "RD",
            dataIndex: "rd",
            width: 100
        },
        {
            text: "Interfaces",
            dataIndex: "interfaces",
            flex: 1,
            renderer: NOC.render.Join(", ")
        },
        {
            text: "Description",
            dataIndex: "description",
            flex: 1
        }
    ],
    search: true
});
