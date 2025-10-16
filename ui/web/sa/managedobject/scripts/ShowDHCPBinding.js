//---------------------------------------------------------------------
// ShowDHCPBinding
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.scripts.ShowDHCPBinding");

Ext.define("NOC.sa.managedobject.scripts.ShowDHCPBinding", {
  extend: "NOC.sa.managedobject.scripts.TablePreview",
  columns: [
    {
      text: __("IP"),
      dataIndex: "ip",
      width: 120,
    },
    {
      text: __("MAC"),
      dataIndex: "mac",
      width: 120,
    },
    {
      text: __("Type"),
      dataIndex: "type",
      width: 50,
    },
    {
      text: __("Expiration time"),
      dataIndex: "expiration",
      flex: 1,
    },
  ],
  search: true,
});
