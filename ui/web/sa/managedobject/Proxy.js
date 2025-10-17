//---------------------------------------------------------------------
// sa.managedobject Proxy
//---------------------------------------------------------------------
// Copyright (C) 2007-2023 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.Proxy");

Ext.define("NOC.sa.managedobject.Proxy", {
  extend: "Ext.data.proxy.Ajax",
  alias: "proxy.managedobject",
  url: "/sa/managedobject/",
  actionMethods: {
    create: "POST",
    read: "GET",
    update: "PUT",
    destroy: "DELETE",
  },
});