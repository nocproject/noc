//---------------------------------------------------------------------
// peer.rir application
//---------------------------------------------------------------------
// Copyright (C) 2007-2011 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.rir.Application");

Ext.define("NOC.peer.rir.Application", {
  extend: "NOC.core.ModelApplication",
  requires: ["NOC.peer.rir.Model"],
  model: "NOC.peer.rir.Model",
  columns: [
    {
      text: __("RIR"),
      dataIndex: "name",
    },
        
    {
      text: __("whois"),
      dataIndex: "whois",
    },
  ],
  fields: [
    {
      name: "name",
      xtype: "textfield",
      fieldLabel: __("name"),
      allowBlank: false,
      uiStyle: "medium",
    },
    {
      name: "whois",
      xtype: "textfield",
      fieldLabel: __("whois"),
      allowBlank: true,
    },
  ],
});
