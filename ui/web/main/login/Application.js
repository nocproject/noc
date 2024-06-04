//---------------------------------------------------------------------
// NOC.main.login.Application 
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.login.Application");
Ext.define("NOC.main.login.Application", {
  extend: "Ext.Viewport",
  // extend: 'Ext.window.Window',
  layout: "fit",
  requires: [
    "Ext.form.Panel",
    "Ext.window.Toast",
  ],
  autoShow: true,
  closable: false,
  resizable: false,
  modal: true,
  defaultListenerScope: true,
  defaultFocus: "user",
  defaultButton: "okButton",
  referenceHolder: true,
  viewModel: "default",
  items: [
    {
      xtype: "panel",
      title: __("NOC Login"),
      layout: "fit",
      padding: "300% 500%",
      items: [
        {
          xtype: "form",
          margin: 0,
          reference: "loginForm",
          border: false,
          fixed: true,
          bodyStyle: {
            background: "#e0e0e0",
            padding: "20 50 0",
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
              fieldLabel: __("Username"),
              blankText: __("User name cannot be empty"),
              // , listeners: {
              //     afterrender: "afterRender"
              // }
            },
            {
              xtype: "textfield",
              itemId: "password",
              name: "password",
              bind: "{password}",
              fieldLabel: __("Password"),
              blankText: __("Password cannot be empty"),
              inputType: "password",
              // , listeners: {
              //     afterrender: "afterRender"
              // }
            },
          ],
          buttons: [
            {
              reference: "okButton",
              formBind: true,
              handler: "onLoginClick",
              text: __("Login"),
              listeners: {
                beforerender: function(){
                  if(!Ext.isIE){
                    Ext.apply(this.autoEl, {type: "submit"})
                  }
                },
              },
            },
          ],
        },
      ],
    },
  ],
  initComponent: function(){
    var param = Ext.urlDecode(location.search);
    if("msg" in param){
      this.items.items[0].value = param.msg + "<br/>" + this.items.items[0].value
    }
    this.callParent();
  },
  afterRender: function(){
    var me = this;
    me.callParent();
    me.hideSplashScreen();
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
      html: "<div style='text-align: center;'>" + __("Failed to log in") + "</div>",
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
    var me = this,
      result = Ext.decode(response.responseText);
    if(result.status === true){
      var param = Ext.urlDecode(location.search);
      if("uri" in param){
        if(location.hash){ // web app
          document.location = "/" + location.hash;
          me.app = Ext.create("NOC.main.desktop.Application");
        } else{ // cards
          document.location = param.uri;
        }
      }
    } else{
      failureFunc();
    }
  },
  hideSplashScreen: function(){
    var mask = Ext.get("noc-loading-mask"),
      parent = Ext.get("noc-loading");
    mask.fadeOut({
      callback: function(){
        mask.destroy();
      },
    });
    parent.fadeOut({
      callback: function(){
        parent.destroy();
      },
    });
  },
});
