//---------------------------------------------------------------------
//  Inspector abstract class
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.map.inspectors.Inspector");

Ext.define("NOC.inv.map.inspectors.Inspector", {
  extend: "Ext.panel.Panel",

  title: undefined,
  scrollable: "vertical",
  defaults: {
    padding: 4,
  },
  inspectorName: undefined,

  getDataURL: function(segmentId){
    var me = this;
    return "/inv/map/info/" + me.inspectorName + "/" + segmentId + "/"
  },

  preview: function(segmentId, objectId){
    var me = this;

    Ext.Ajax.request({
      url: me.getDataURL(segmentId, objectId),
      method: "GET",
      scope: me,
      success: function(response){
        var values = Ext.decode(response.responseText);
        this.update(values);
        this.enableButtons(values);
      },
    });
  },

  enableButtons: Ext.emptyFn,
});
