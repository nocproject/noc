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
  title: __("Create Item"),
  modal: true,
  closeAction: "hide",
  layout: "fit",
  items: [
    {
      xtype: "form",
      bodyPadding: 10,
      defaults: {
        anchor: "100%",
        labelWidth: 100,
      },
      items: [
        {
          xtype: "hiddenfield",
          name: "channel_id",
        },
        {
          xtype: "textfield",
          name: "name",
          fieldLabel: __("Name"),
          allowBlank: false,
        },
        {
          xtype: "checkbox",
          name: "dry_run",
          inputValue: true,
          uncheckedValue: false,
          fieldLabel: __("Dry Run"),
        },
      ],
      buttons: [
        {
          formBind: true,
          disabled: true,
          bind: {
            text: "{createInvChannelBtnText}",
          },
          handler: function(button){
            var form = button.up("form").getForm();
            if(form.isValid()){
              var values = form.getValues();
              this.up("invChannelParamsForm").fireEvent("complete", values);
              button.up("window").hide();
            }
          },
        },
        {
          text: __("Close"),
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
  },
});
