//---------------------------------------------------------------------
// main.welcome application
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.welcome.Application");

Ext.define("NOC.main.welcome.Application", {
  extend: "NOC.core.Application",
  appId: "main.welcome",
  bodyPadding: 4,

  afterRender: function(){
    var me = this;
    me.callParent();
    Ext.Ajax.request({
      url: "/main/welcome/welcome/",
      method: "GET",
      scope: me,
      success: function(response){
        me.setHtml(response.responseText);
      },
    });
  },
});
