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
              NOC.run(
                "NOC.inv.map.Maintenance",
                __("Add To Maintenance"),
                {
                  args: [
                    {mode: "Object"},
                    Ext.Array.map(alarms, function(alarm){
                      return {
                        object: alarm.managed_object,
                        object__label: alarm.managed_object__label,
                      }
                    }),
                  ],
                },
              );
            }
          } else{
            NOC.error(data.message || __("Failed to clear alarms"));
          }
        },
        failure: function(){
          NOC.error(__("Backend: failed to clear alarms"));
        },
        callback: function(){
          form.unmask();
        },
      });
    },
  }],
});