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
      text: __("Name"),
      dataIndex: "name",
      width: 120,
    },
    {
      text: __("Status"),
      dataIndex: "status",
      width: 50,
      renderer: NOC.render.Bool,
    },
    {
      text: __("Type"),
      dataIndex: "type",
      width: 70,
    },
    {
      text: __("RD"),
      dataIndex: "rd",
      width: 100,
    },
    {
      text: __("RT Export"),
      dataIndex: "rt_export",
      width: 200,
    },
    {
      text: __("RT Import"),
      dataIndex: "rt_import",
      width: 200,
    },
    {
      text: __("Interfaces"),
      dataIndex: "interfaces",
      flex: 1,
      renderer: NOC.render.Join(", "),
    },
    {
      text: __("Description"),
      dataIndex: "description",
      flex: 1,
    },
  ],
  search: true,
});
