//---------------------------------------------------------------------
// Diagnostic plugin
//---------------------------------------------------------------------
// Copyright (C) 2007-2016 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.alarm.plugins.Diagnostic");

Ext.define("NOC.fm.alarm.plugins.Diagnostic", {
  extend: "Ext.panel.Panel",
  title: __("Diagnostic"),
  app: null,
  autoScroll: true,
  bodyPadding: 4,
  stateMap: {
    "R": __("Raise"),
    "C": __("Clear"),
    "P": __("Periodic"),
  },

  updateData: function(data){
    var me = this,
      html = [];
    Ext.each(data.diagnostic, function(r){
      html.push("<b>[" + me.stateMap[r.state] + "] " + r.timestamp + "</b><br>");
      html.push("<pre>" + r.data + "</pre><br>");
    });
    me.setHtml(html.join("\n"));
  },
});


