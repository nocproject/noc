//---------------------------------------------------------------------
// peer.peergroup application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.peergroup.Application");

Ext.define("NOC.peer.peergroup.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.peer.peergroup.Model",
  ],
  model: "NOC.peer.peergroup.Model",
  search: true,
  columns: [
    {
      text: __("Name"),
      dataIndex: "name",
      flex: 1,
    },

    {
      text: __("Description"),
      dataIndex: "description",
      flex: 1,
    },
    {
      text: __("Import Communities"),
      dataIndex: "communities",
      flex: 1,
    },
  ],
  fields: [
    {
      name: "name",
      xtype: "textfield",
      fieldLabel: __("Name"),
      allowBlank: false,
      width: 300,
    },
    {
      name: "description",
      xtype: "textfield",
      fieldLabel: __("Description"),
      allowBlank: false,
      width: 300,
    },
    {
      name: "communities",
      xtype: "textfield",
      fieldLabel: __("Import Communities"),
      allowBlank: true,
      width: 300,
    },
    {
      name: "max_prefixes",
      xtype: "textfield",
      maskRe: /\d/i,
      fieldLabel: __("Max. Prefixes"),
      allowBlank: false,
    },
    {
      name: "local_pref",
      xtype: "textfield",
      maskRe: /\d/i,
      fieldLabel: __("Local Pref"),
      allowBlank: true,
    },
    {
      name: "import_med",
      xtype: "textfield",
      maskRe: /\d/i,
      fieldLabel: __("Import MED"),
      allowBlank: true,
    },
    {
      name: "export_med",
      xtype: "textfield",
      maskRe: /\d/i,
      fieldLabel: __("Export MED"),
      allowBlank: true,
    },
  ],
  filters: [
  ],
});
