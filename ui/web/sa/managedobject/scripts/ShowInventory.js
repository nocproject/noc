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
      text: __("Type"),
      dataIndex: "type",
      width: 90,
    },
    {
      text: __("Number"),
      dataIndex: "number",
      width: 50,
    },
    {
      text: __("Builtin"),
      dataIndex: "builtin",
      width: 50,
      renderer: NOC.render.Bool,
    },
    {
      text: __("Vendor"),
      dataIndex: "vendor",
      width: 90,
    },
    {
      text: __("Part No"),
      dataIndex: "part_no",
      width: 230,
    },
    {
      text: __("Revision"),
      dataIndex: "revision",
      width: 70,
    },
    {
      text: __("Serial No"),
      dataIndex: "serial",
      width: 120,
    },
    {
      text: __("Description"),
      dataIndex: "description",
      flex: 1,
    },
  ],
  search: true,
});
