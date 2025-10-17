//---------------------------------------------------------------------
// ShowPortChannel
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.scripts.ShowPortChannel");

Ext.define("NOC.sa.managedobject.scripts.ShowPortChannel", {
  extend: "NOC.sa.managedobject.scripts.TablePreview",
  columns: [
    {
      text: __("Interface"),
      dataIndex: "interface",
      width: 100,
    },
    {
      text: __("Members"),
      dataIndex: "members",
      width: 200,
    },
    {
      text: __("Type"),
      dataIndex: "type",
      flex: 1,
    },
  ],
  search: true,
});
