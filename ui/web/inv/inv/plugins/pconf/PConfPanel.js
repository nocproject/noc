//---------------------------------------------------------------------
// inv.inv PConf Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.pconf.PConfPanel");

Ext.define("NOC.inv.inv.plugins.pconf.PConfPanel", {
  extend: "Ext.panel.Panel",
  requires: [
    "NOC.inv.inv.plugins.pconf.PConfModel",
  ],
  title: __("Config"),
  closable: false,
  layout: "fit",

  initComponent: function(){
    var me = this;

    // Data Store
    me.store = Ext.create("Ext.data.Store", {
      model: "NOC.inv.inv.plugins.pconf.PConfModel",
    });
    // Grids
    Ext.apply(me, {
      items: [
        {
          xtype: "gridpanel",
          border: false,
          autoScroll: true,
          stateful: true,
          store: me.store,
          columns: [
            {
              text: __("Name"),
              dataIndex: "name",
              width: 150,
            },
            {
              text: __("Value"),
              dataIndex: "value",
              width: 150,
            },
            {
              text: __("Units"),
              dataIndex: "units",
              width: 50,
            },
            {
              text: __("Description"),
              dataIndex: "description",
              flex: 1,
            },
          ],
        },
      ],
    });
    me.callParent();
  },
  //
  preview: function(data){
    var me = this;
    me.currentId = data.id;
    console.log(">>>", data);
    me.store.loadData(data.conf);
  },
});
