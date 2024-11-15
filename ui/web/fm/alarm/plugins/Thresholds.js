//---------------------------------------------------------------------
// Validation plugin
//---------------------------------------------------------------------
// Copyright (C) 2007-2015 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.plugins.Validation");

Ext.define("NOC.fm.alarm.plugins.Thresholds", {
  extend: "Ext.panel.Panel",
  title: __("Thresholds"),
  app: null,
  autoScroll: true,
  bodyPadding: 4,

  initComponent: function(){
    var me = this;

    me.store = Ext.create("Ext.data.Store", {
      fields: [
        "name", "interface", "value", "level",
      ],
      data: [],
    });

    me.grid = Ext.create("Ext.grid.Panel", {
      autoScroll: true,
      store: me.store,
      columns: [
        {
          dataIndex: "name",
          text: __("Metric"),
          width: 150,
        },
        {
          dataIndex: "interface",
          text: __("Interface"),
          width: 150,
        },
        {
          dataIndex: "level",
          text: __("Level"),
          width: 50,
        },
        {
          dataIndex: "value",
          text: __("Value"),
          width: 100,
          renderer: NOC.render.Size,
        },
        {
          dataIndex: "condition",
          text: __("Condition"),
          width: 50,
        },
        {
          dataIndex: "threshold",
          text: __("Threshold"),
          flex: 1,
          renderer: NOC.render.Size,
        },
      ],
    });

    Ext.apply(me, {
      items: [
        me.grid,
      ],
    });

    me.callParent();
  },

  updateData: function(data){
    var me = this;
    me.store.loadData(data.thresholds);
  },
});
