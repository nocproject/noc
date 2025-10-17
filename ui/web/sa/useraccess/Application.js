//---------------------------------------------------------------------
// sa.useraccess application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.useraccess.Application");

Ext.define("NOC.sa.useraccess.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.sa.useraccess.Model",
    "NOC.aaa.user.LookupField",
    "NOC.sa.administrativedomain.LookupField",
  ],
  model: "NOC.sa.useraccess.Model",
  columns: [
    {
      text: __("User"),
      dataIndex: "user",
      renderer: NOC.render.Lookup("user"),
    },
    {
      text: __("Adm. Domain"),
      dataIndex: "administrative_domain",
      renderer: NOC.render.Lookup("administrative_domain"),
    },
  ],
  fields: [
    {
      name: "user",
      xtype: "aaa.user.LookupField",
      fieldLabel: __("User"),
      allowBlank: false,
    },
    {
      name: "administrative_domain",
      xtype: "sa.administrativedomain.LookupField",
      fieldLabel: __("Adm. Domain"),
      allowBlank: true,
    },
  ],
  filters: [
    {
      title: __("By User"),
      name: "user",
      ftype: "lookup",
      lookup: "aaa.user",
    },
    {
      title: __("By Administrative Domain"),
      name: "administrative_domain",
      ftype: "lookup",
      lookup: "sa.administrativedomain",
    },
  ],
});
