//---------------------------------------------------------------------
// inv.inv Alarm Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.alarm.AlarmPanel");

Ext.define("NOC.inv.inv.plugins.alarm.AlarmPanel", {
  extend: "Ext.panel.Panel",
  requires: [
    "NOC.inv.inv.plugins.alarm.AlarmModel",
  ],

  title: __("Alarms"),
  closable: false,
  layout: "fit",
  //
  initComponent: function(){
    var me = this;

    me.defaultRoot = {
      text: __("."),
      children: [],
    };

    me.store = Ext.create("Ext.data.TreeStore", {
      model: "NOC.inv.inv.plugins.alarm.AlarmModel",
      root: me.defaultRoot,
    });

    me.alarmPanel = Ext.create("Ext.tree.Panel", {
      store: me.store,
      rootVisible: false,
      useArrows: true,
      stateful: true,
      stateId: "inv.inv-alarm-alarm",
      columns: [
        {
          xtype: "treecolumn",
          dataIndex: "title",
          text: __("Title"),
          width: 400,
        },
        {
          text: __("Alarm Class"),
          dataIndex: "alarm_class",
          width: 300,
        },
      ],
    });
    //
    Ext.apply(me, {
      items: [
        me.alarmPanel,
      ],
    });
    me.callParent();
  },
  //
  preview: function(data, objectId){
    var me = this;
    me.store.setRootNode(data || me.defaultRoot)
  },
});