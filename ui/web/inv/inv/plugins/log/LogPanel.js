//---------------------------------------------------------------------
// inv.inv Log Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.log.LogPanel");

Ext.define("NOC.inv.inv.plugins.log.LogPanel", {
  extend: "Ext.panel.Panel",
  requires: [
    "NOC.inv.inv.plugins.log.LogModel",
  ],
  title: __("Log"),
  closable: false,
  layout: "fit",

  initComponent: function(){
    var me = this;

    // Data Store
    me.store = Ext.create("Ext.data.Store", {
      model: "NOC.inv.inv.plugins.log.LogModel",
    });
    // Grids
    Ext.apply(me, {
      items: [
        {
          xtype: "gridpanel",
          border: false,
          autoScroll: true,
          stateful: true,
          stateId: "inv.inv-log-grid",
          store: me.store,
          columns: [
            {
              text: __("Time"),
              dataIndex: "ts",
              renderer: NOC.render.DateTime,
              width: 100,
            },
            {
              text: __("User"),
              dataIndex: "user",
              width: 70,
            },
            {
              text: __("System"),
              dataIndex: "system",
              width: 70,
            },
            {
              text: __("Operation"),
              dataIndex: "op",
              width: 70,
            },
            {
              text: __("Object"),
              dataIndex: "managed_object",
              width: 100,
            },
            {
              text: __("Message"),
              dataIndex: "message",
              flex: 1,
            },
          ],
          viewConfig: {
            enableTextSelection: true,
          },
        },
      ],
    });
    me.callParent();
  },
  //
  preview: function(data){
    var me = this;
    me.currentId = data.id;
    me.store.loadData(data.log);
  },
  //
  onReload: function(){
    var me = this;
    Ext.Ajax.request({
      url: "/inv/inv/" + me.currentId + "/plugin/log/",
      method: "GET",
      scope: me,
      success: function(response){
        me.preview(Ext.decode(response.responseText));
      },
      failure: function(){
        NOC.error(__("Failed to get data"));
      },
    });
  },
});
