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
        xtype: "textfield",
        itemId: "user",
        name: "user",
        bind: "{user}",
        fieldLabel: __("User"),
        blankText: __("User name cannot be empty"),
      },
      {
        xtype: "textfield",
        itemId: "password",
        name: "password",
        bind: "{password}",
        fieldLabel: __("Password"),
        blankText: __("Password cannot be empty"),
        inputType: "password",
      },
    ],
    buttons: [{
      reference: "okButton",
      formBind: true,
      handler: "onLoginClick",
      text: __("Login"),
      listeners: {
        beforerender: function(){
          Ext.apply(this.autoEl, {type: "submit"});
        },
      },
    }],
  },
  initComponent: function(){
    var param = Ext.urlDecode(location.search);
    if("msg" in param){
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
      Ext.Ajax.request({
        url: "/api/login/login",
        params: params,
        method: "POST",
        success: Ext.Function.pass(this.onLoginSuccess, this.onLoginFailure),
        failure: this.onLoginFailure,
        defaultPostHeader: "application/json",
      });
    }
  },
  onLoginFailure: function(){
    Ext.toast({
      html: '<div style="text-align: center;">' + __("Failed to log in") + "</div>",
      align: "t",
      paddingY: 0,
      width: "80%",
      minHeight: 5,
      border: false,
      listeners: {
        focusenter: function(){
          this.close();
        },
      },
      bodyStyle: {
        color: "white",
        background: "red",
        "font-weight": "bold",
      },
      style: {
        background: "red",
        "border-width": "0px",
      },
    });
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
