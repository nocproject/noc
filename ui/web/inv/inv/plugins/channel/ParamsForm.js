//---------------------------------------------------------------------
// inv.inv Channel Param Form
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.channel.ParamsForm");

Ext.define("NOC.inv.inv.plugins.channel.ParamsForm", {
  extend: "Ext.window.Window",
  xtype: "invChannelParamsForm",
  defaultListenerScope: true,
  title: __("Create Item"),
  modal: true,
  closeAction: "hide",
  layout: "fit",
  items: [
    {
      xtype: "form",
      submitEmptyText: false,
      bodyPadding: 10,
      defaultFocus: "name",
      defaults: {
        anchor: "100%",
        labelWidth: 200,
        listeners: {
          specialkey: "onSpecialKey",
        },
      },
      items: [
      ],
      buttons: [
        {
          glyph: NOC.glyph.save,
          formBind: true,
          disabled: true,
          bind: {
            text: "{createInvChannelBtnText}",
          },
          handler: "onCreateChannel",
        },
        {
          text: __("Close"),
          glyph: NOC.glyph.times,
          handler: function(button){
            button.up("window").hide();
          },
        },
      ],
    },
  ],
  listeners: {
    beforerender: function(win){
      var parent = win.up();
      if(parent){
        var parentWidth = parent.getWidth();
        var parentHeight = parent.getHeight();
        win.setWidth(parentWidth * 0.8);
        win.setHeight(parentHeight * 0.8);
      }
    },
    resize: function(win){
      var parent = win.up();
      if(parent){
        var parentWidth = parent.getWidth();
        var parentHeight = parent.getHeight();
        win.setWidth(parentWidth * 0.8);
        win.setHeight(parentHeight * 0.8);
      }
    },
    show: function(win){
      Ext.defer(function(){
        win.down("[name=name]").focus();
      }, 50);
    },
  },
  onSpecialKey: function(field, e){
    if(e.getKey() === e.ENTER){
      this.onCreateChannel(field);
    }
  },
  onCreateChannel: function(field){
    var form = field.up("form").getForm();
    if(form.isValid()){
      var values = this.extractData(form.getValues());
      if(Ext.isEmpty(values.channel_id)){
        delete values.channel_id;
      }
      form.reset();
      this.fireEvent("complete", values);
      field.up("window").hide();
    }
  },
  extractData: function(data){
    var result = {}, params = {};
    Ext.Object.each(data, function(key, value){
      if(key.indexOf("params.") === 0){
        params[key.substr(7)] = value;
      } else{
        result[key] = value;
      }
    });
    if(!Ext.Object.isEmpty(params)){
      result.params = params;
    }
    return result;
  },
});
