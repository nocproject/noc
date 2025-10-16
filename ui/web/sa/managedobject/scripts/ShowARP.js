//---------------------------------------------------------------------
// ShowARP
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.scripts.ShowARP");

Ext.define("NOC.sa.managedobject.scripts.ShowARP", {
  extend: "NOC.sa.managedobject.scripts.TablePreview",
  columns: [
    {
      text: __("IP"),
      dataIndex: "ip",
      width: 100,
    },
    {
      text: __("MAC"),
      dataIndex: "mac",
      width: 120,
    },
    {
      text: __("Interface"),
      dataIndex: "interface",
      flex: 1,
    },
  ],
  search: true,
});
