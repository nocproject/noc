//---------------------------------------------------------------------
// Application UI
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC application");

Ext.application({
  name: "NOC",
  paths: {
    "NOC": "/ui/web",
    "Ext.ux": "/ui/web/ux",
  },

  requires: [
    "NOC.main.desktop.Application",
    "NOC.main.login.Application",
  ],

  launch: function(){
    var me = this;
    Ext.setGlyphFontFamily("FontAwesome");
    console.log("Initializing history API");
    Ext.History.init();
    console.log("NOC application starting");
    Ext.Ajax.request({
      method: "GET",
      url: "/api/login/is_logged/",
      scope: me,
      success: function(response){
        var status = Ext.decode(response.responseText);
        if(status){
          // Create viewport
          me.app = Ext.create("NOC.main.desktop.Application");
        } else{
          Ext.create("NOC.main.login.Application");
          NOC.error(__("Login failed"));
        }
      },
      failure: function(){
        NOC.error(__("Login failed"));
      },
    });
  },
});
