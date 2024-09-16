//---------------------------------------------------------------------
// inv.inv Channel Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.bom.BoMPanel");

Ext.define("NOC.inv.inv.plugins.bom.BoMPanel", {
  extend: "Ext.panel.Panel",
  title: __("BoM"),
  closable: false,
  defaultListenerScope: true,
  items: [
    {
      xtype: "grid",
      scrollable: "y",
      columns: [
      ],
    },
  ],
  preview: function(data, objectId){
    var me = this,
      grid = me.down("grid"),
      records = data.data || [];
    me.currentId = objectId;
    grid.getStore().loadData(records);
  },
});
