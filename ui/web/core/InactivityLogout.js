//---------------------------------------------------------------------
// Inactivity Logout
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.InactivityLogout");

Ext.define("NOC.core.InactivityLogout", {
  singleton: true,
  inactivityTimeout: 60 * 60 * 1000, // 1 hour
  timeoutTask: null,
  //
  init: function(timeout){
    this.inactivityTimeout = timeout * 1000 || this.inactivityTimeout;
    this.attachActivityListeners();
    this.resetTimeout();
  },
  //
  attachActivityListeners: function(){
    const listeners = {},
      events = ["mousemove", "keydown", "mousedown", "touchstart", "scroll"];
      
    events.forEach((eventName) => {
      listeners[eventName] = {
        fn: this.resetTimeout,
        scope: this,
        buffer: 10 * 1000, // 10 seconds
      };
    });
    Ext.getDoc().on(listeners);
  },
  //
  resetTimeout: function(){
    if(this.timeoutTask){
      clearTimeout(this.timeoutTask);
    }    
    this.timeoutTask = setTimeout(this.onInactivityTimeout.bind(this), this.inactivityTimeout);
  },
  //
  onInactivityTimeout: function(){
    this.logout(); },
  //
  logout: function(){
    Ext.Ajax.request({
      url: "/api/login/logout/",
      method: "GET",
      scope: this,
      callback: function(){
        this.showSessionTimeoutMessage();
      },
    });
  },
  //
  showSessionTimeoutMessage: function(){
    Ext.Msg.show({
      title: __("Session Expired"),
      message: __("Your session has expired due to inactivity.<br/><br/>") +
        __("You have been automatically logged out of the application for security reasons.<br/><br/>") +
        __("Please log in again to continue."),
      buttons: Ext.Msg.OK,
      icon: Ext.Msg.ERROR,
      modal: true,
      closable: false,
      resizable: false,
      width: 500,  
      buttonText: {
        ok: __("Login Again"),
      },  
      fn: function(btn){
        if(btn === "ok"){
          NOC.app.app.onLogout("Autologout");
        }
      },
    });
  },
});