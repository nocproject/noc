// main.desktop.ChangePassword
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.ChangePassword");

Ext.define("NOC.main.desktop.ChangePassword", {
  extend: "Ext.window.Window",
  xtype: "changePassword",
  autoShow: true,
  closable: false,
  resizable: false,
  title: __("Change Password"),
  layout: "fit",
  modal: true,
  defaultListenerScope: true,
  width: 500,
  height: 310,
  viewModel: "default",
  items: {
    xtype: "form",
    reference: "changePasswordForm",
    fixed: true,
    border: false,
    bodyStyle: {
      background: "#e0e0e0",
      padding: "20px",
    },
    autoEl: {
      tag: "form",
    },
    defaults: {
      anchor: "100%",
      allowBlank: false,
      enableKeyEvents: true,
      xtype: "textfield",
      inputType: "password",
    },
    layout: {
      type: "vbox",
      align: "stretch",
      pack: "center",
    },
    items: [
      {
        itemId: "oldPass",
        name: "oldPass",
        bind: "{oldPass}",
        fieldLabel: __("Old Password"),
        blankText: __("Old Password cannot be empty"),
      },
      {
        itemId: "newPass",
        name: "newPass",
        bind: "{newPass}",
        fieldLabel: __("New Password"),
        blankText: __("New Password cannot be empty"),
      },
      {
        itemId: "confirmPass",
        name: "confirmPass",
        bind: "{confirmPass}",
        fieldLabel: __("Confirm New Password"),
        blankText: __("Please confirm your new password"),
        validator: function(value){
          var newPass = this.up("form").down("#newPass").getValue();
          return value === newPass ? true : __("Passwords do not match");
        },
      },
    ],
    buttons: [
      {
        reference: "okButton",
        formBind: true,
        handler: "onChangeClick",
        text: __("Change"),
        glyph: "xf090@FontAwesome",
        listeners: {
          beforerender: function(){
            Ext.apply(this.autoEl, {type: "submit"});
          },
        },
      },
    ],
  },
  onChangeClick: function(field){
    var form = field.up("form").getForm();
    if(form.isValid()){
      Ext.Ajax.request({
        url: "/api/login/change_credentials",
        method: "POST",
        jsonData: {
          user: this.username,
          old_password: form.findField("oldPass").getValue(),
          new_password: form.findField("newPass").getValue(),
        },
        success: function(response){
          var data = Ext.decode(response.responseText);
          if(data.status){
            NOC.msg.complete(__("Password changed"));
            this.close();
          } else{
            NOC.error(__("Error changing password"));
          }
        },
        failure: function(){
          NOC.error(__("Error changing password"));
        },
      });
    }
  },
});