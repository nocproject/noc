//---------------------------------------------------------------------
// fm.alarm application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.view.form.ClearAlarms");

Ext.define("NOC.fm.alarm.view.form.ClearAlarms", {
  extend: "Ext.window.Window",
  alias: "widget.fm.alarm.clearwindow",

  requires: [
    "Ext.form.Panel",
    "Ext.form.field.TextArea",
    "Ext.form.field.ComboBox",
  ],

  title: __("Clear alarms"),
  modal: true,
  itemId: "fmAlarmClear",
  width: 400,
  layout: "fit",
    
  items: [{
    xtype: "form",
    bodyPadding: 10,
    items: [{
      xtype: "textarea",
      fieldLabel: __("Message"),
      name: "message",
      allowBlank: false,
      width: "100%",
      listeners: {
        change: function(field, value){
          this.up("window").down("#clearBtn").setDisabled(!value.trim());
        },
      },
    }, {
      xtype: "checkbox",
      fieldLabel: __("Create maintenance"),
      name: "maintenance",
      value: false,
    }],
  }],
    
  buttons: [{
    text: __("Cancel"),
    glyph: NOC.glyph.times, 
    handler: function(){
      this.up("window").close();
    },
  }, {
    itemId: "clearBtn",
    text: __("Clear"),
    glyph: NOC.glyph.minus, 
    disabled: true,
    handler: function(){
      var win = this.up("window"),
        form = win.down("form"),
        values = form.getValues(),
        alarms = this.up("[itemId=fmAlarmClear]").alarms;

      form.mask(__("Clearing alarms..."));
      Ext.Ajax.request({
        url: "/fm/alarm/clear/",
        method: "POST",
        jsonData: {
          msg: values.message,
          alarms: Ext.Array.map(alarms, function(record){return record.id}),
        },
        success: function(response){
          var data = Ext.decode(response.responseText);
          if(data.status){
            win.close();
            win.parentController.reloadActiveGrid();
            NOC.info(__("Alarms cleared successfully"));
            if(values.maintenance){
              var objects = Ext.Array.map(alarms, function(alarm){
                  return {
                    object: alarm.managed_object,
                    object__label: alarm.managed_object__label,
                  }
                }),
                args = {
                  direct_objects: objects,
                  subject: __("created from alarm list at ") + Ext.Date.format(new Date(), "d.m.Y H:i P"),
                  contacts: NOC.email ? NOC.email : NOC.username,
                  start_date: Ext.Date.format(new Date(), "d.m.Y"),
                  start_time: Ext.Date.format(new Date(), "H:i"),
                  stop_time: "12:00",
                  suppress_alarms: true,
                };
              Ext.create("NOC.maintenance.maintenancetype.LookupField")
            .getStore()
            .load({
              params: {__query: "РНР"},
              callback: function(records){
                if(records.length > 0){
                  Ext.apply(args, {
                    type: records[0].id,
                  })
                }
                NOC.launch("maintenance.maintenance", "new", {
                  args: args,
                });
              },
            });
            }
          } else{
            NOC.error(data.message || __("Failed to clear alarms"));
          }
        },
        failure: function(){
          NOC.error(__("Backend: failed to clear alarms"));
          form.unmask();
        },
        callback: function(){
        },
      });
    },
  }],
});