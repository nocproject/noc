//---------------------------------------------------------------------
// inv.inv Commutation Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.commutation.CommutationPanel");

Ext.define("NOC.inv.inv.plugins.commutation.CommutationPanel", {
  extend: "Ext.panel.Panel",
  title: __("Commutation"),
  closable: false,
  layout: "fit",
  initComponent: function(){
    var me = this;
    me.callParent();
  },
  //
  preview: function(data){
    var me = this;
    if(typeof Viz === "undefined"){
      new_load_scripts([
        'https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/viz.js',
        'https://cdnjs.cloudflare.com/ajax/libs/viz.js/2.1.2/full.render.js',          
      ], me, function(){
        me.renderScheme(data.dot);
      });
    } else{
      me.renderScheme(data.dot);
    }
  },
  renderScheme: function(dot){
    var me = this,
      viz=new Viz();
    viz.renderSVGElement(dot).then(function(el){
      me.removeAll();
      me.add({
        xtype: "component",
        autoScroll: true,
        html: el.outerHTML,
      });
    });
  },
  //
  onReload: function(){
    var me = this;
    Ext.Ajax.request({
      url: "/inv/inv/" + me.currentId + "/plugin/commutation/",
      method: "GET",
      scope: me,
      success: function(response){
        me.preview(Ext.decode(response.responseText));
      },
      failure: function(){
        NOC.error(__("Failed to get data"));
      },
    });
  },
});
