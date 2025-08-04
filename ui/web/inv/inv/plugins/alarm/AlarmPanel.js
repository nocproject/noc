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
          renderer: NOC.render.Lookup("alarm_class"),
        },
        {
          text: __("Severity"),
          dataIndex: "severity",
          width: 70,
          renderer: function(v, _, record){
            return record.get("severity__label") +
                    "<br/>" +
                    record.get("severity");
          },
        },
        {
          text: __("Time/Duration"),
          dataIndex: "timestamp",
          width: 120,
          renderer: function(v, _, record){
            return NOC.render.DateTime(record.get("timestamp")) +
                    "<br/>" +
                    NOC.render.Duration(record.get("duration"));
          },
        },
        {
          text: __("Channel"),
          dataIndex: "channel",
          width: 300,
          renderer: NOC.render.Lookup("channel"),
        },
        {
          text: __("Object"),
          dataIndex: "object",
          flex: 1,
          renderer: function(v){
            return v.map(function(x){return x["title"]}).join(" > ");
          },
        },
      ],
      viewConfig: {
        getRowClass: Ext.bind(me.getRowClass, me),
      },
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
  // Return Grid's row classes
  getRowClass: function(record, index, params, store){
    var c = record.get("row_class");
    if(c){
      return c;
    } else{
      return "";
    }
  },
});