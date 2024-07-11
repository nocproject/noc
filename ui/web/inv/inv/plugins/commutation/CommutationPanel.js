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
  defaultListenerScope: true,
  tbar: [
    {
      xtype: "combobox",
      store: [
        [0.25, "25%"],
        [0.5, "50%"],
        [0.75, "75%"],
        [1.0, "100%"],
        [1.25, "125%"],
        [1.5, "150%"],
        [2.0, "200%"],
        [3.0, "300%"],
        [4.0, "400%"],
      ],
      width: 100,
      value: 1.0,
      valueField: "zoom",
      displayField: "label",
      listeners: {
        select: "onZoom",
      },    
    }],
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
        xtype: "container",
        layout: "fit",
        items: {
          xtype: "image",
          itemId: "scheme",
          src: me.svgToBase64(el.outerHTML),
        },
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
  //
  onZoom: function(combo){
    var me = this,
      imageComponent = me.down("#scheme");
    imageComponent.getEl().dom.style.transformOrigin = "0 0";
    imageComponent.getEl().dom.style.transform = "scale(" + combo.getValue() + ")";
  },
  //
  svgToBase64: function(svgString){
    var base64String = "data:image/svg+xml;base64," + btoa(svgString);
    return base64String;
  },
});
