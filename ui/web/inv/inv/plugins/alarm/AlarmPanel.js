//---------------------------------------------------------------------
// inv.inv Alarm Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.alarm.AlarmPanel");

Ext.define("NOC.inv.inv.plugins.alarm.AlarmPanel", {
  extend: "Ext.panel.Panel",
  title: __("Alarms"),
  closable: false,
  layout: "fit",
  //
  initComponent: function(){
    this.callParent();
  },
  //
  preview: function(data, objectId){
    
  },
});