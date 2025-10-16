//---------------------------------------------------------------------
// peer.community application
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.peer.community.Application");

Ext.define("NOC.peer.community.Application", {
  extend: "NOC.core.ModelApplication",
  requires: ["NOC.peer.community.Model",
             "NOC.peer.communitytype.LookupField",
  ],
  model: "NOC.peer.community.Model",
  search: true,
  columns: [
    {
      text: __("Community"),
      dataIndex: "community",
      flex: 1,
    },
    {
      text: __("Type"),  
      dataIndex: "type",
      renderer: NOC.render.Lookup("type"),
      flex: 1,
    },
    {
      text: __("Description"),  
      dataIndex: "description",
      flex: 1,
    },
  ],
  fields: [
    {
      name: "community",
      xtype: "textfield",
      fieldLabel: __("Community"),
      width: 400,
      allowBlank: false,
    },
    {
      name: "type",
      xtype: "peer.communitytype.LookupField",
      fieldLabel: __("Type"),
      width: 400,
      allowBlank: false,
    },
    {
      name: "description",
      xtype: "textfield",
      fieldLabel: __("Description"),  
      width: 400,
      allowBlank: false,
    }, 
  ],
  filters: [
    {
      title: __("By Community Type"),
      name: "type",
      ftype: "lookup",
      lookup: "peer.communitytype",
    },
  ],
});
