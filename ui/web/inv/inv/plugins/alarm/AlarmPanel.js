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
            if(v && v.length > 0){
              return v.map(function(x){
                let html = "<span";
                if(!Ext.isEmpty(x.id)){
                  html += ` class="noc-clickable-object"  data-object-id="${x.id}"`;
                }
                return html + `>${x.title}</span>`;
              }).join(" > ");
            }
            return "";
          },  
        },
      ],
      viewConfig: {
        getRowClass: Ext.bind(me.getRowClass, me),
      },
      listeners: {
        scope: this,
        afterrender: function(panel){
          panel.getEl().on("click", function(e, target){
            var objectId = target.getAttribute("data-object-id");
            if(objectId){
              this.up("[appId]").showObject(objectId);
            }
          }, this, {
            delegate: ".noc-clickable-object",
            stopEvent: true,
          });
        },
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
  preview: function(data){
    var me = this;
    me.store.setRootNode(data || me.defaultRoot)
  },
  // Return Grid's row classes
  getRowClass: function(record){
    var c = record.get("row_class");
    if(c){
      return c;
    } else{
      return "";
    }
  },
});