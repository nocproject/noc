//---------------------------------------------------------------------
// main.desktop.Login 
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.desktop.LoginView");

Ext.define("NOC.main.desktop.LoginView", {
  extend: "Ext.window.Window",
  xtype: "login",
  autoShow: true,
  closable: false,
  resizable: false,
  title: __("NOC Login"),
  layout: "fit",
  modal: true,
  defaultListenerScope: true,
  defaultFocus: "user",
  defaultButton: "okButton",
  referenceHolder: true,
  width: 500,
  height: 310,
  viewModel: "default",
  items: {
    xtype: "form",
    reference: "loginForm",
    fixed: true,
    border: false,
    bodyStyle: {
      background: "#e0e0e0",
      padding: "10px",
    },
    autoEl: {
      tag: "form",
    },
    defaults: {
      anchor: "100%",
      allowBlank: false,
      enableKeyEvents: true,
      xtype: "textfield",
    },
    items: [
      {
        xtype: "displayfield",
        value: __("Type username and password:"),
        hideLabel: true,
      },
      {
        itemId: "user",
        name: "user",
        bind: "{user}",
        fieldLabel: __("User"),
        blankText: __("User name cannot be empty"),
      },
      {
        itemId: "password",
        name: "password",
        bind: "{password}",
        fieldLabel: __("Password"),
        blankText: __("Password cannot be empty"),
        inputType: "password",
      },
    ],
    buttons: [
      {
        reference: "okButton",
        formBind: true,
        handler: "onLoginClick",
        text: __("Login"),
        glyph: "xf090@FontAwesome",
        listeners: {
          beforerender: function(){
            Ext.apply(this.autoEl, {type: "submit"});
          },
        },
      },
      {
        itemId: "resetBtn",
        text: __("Reset"),
        glyph: "xf00d@FontAwesome",
        handler: function(){
          this.up("form").reset();
        },
      },
    ],
  },
  initComponent: function(){
    var param = Ext.urlDecode(location.search);
    if("msg" in param){ // show message when timeout
      this.items.items[0].value = param.msg + "<br/>" + this.items.items[0].value;
    }
    this.callParent();
  },
  onLoginClick: function(){
    var data = this.getViewModel().getData(),
      params = Ext.encode({
        user: data.user,
        password: data.password,
      });
    if(params !== undefined){
      this.lookup("loginForm").setDisabled(true);
      Ext.Ajax.request({
        url: "/api/login/login",
        params: params,
        method: "POST",
        scope: this,
        success: Ext.Function.pass(this.onLoginSuccess, this.onLoginFailure),
        failure: this.onLoginFailure,
        callback: function(){
          this.lookup("loginForm").setDisabled(false);
        },
        defaultPostHeader: "application/json",
      });
    }
  },
  onLoginFailure: function(){
    NOC.error(__("Failed to log in"));
  },
  onLoginSuccess: function(failureFunc, response){
    var result = Ext.decode(response.responseText);
    if(result.status === true){
      var param = Ext.urlDecode(location.search);
      if("uri" in param){
        if(location.hash){ // web app
          location = "/" + location.hash;
        } else{ // cards
          location = param.uri;
        }
      }
    } else{
      failureFunc();
    }
  },
});
