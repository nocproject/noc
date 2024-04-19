//---------------------------------------------------------------------
// inv.inv Facade panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.facade.FacadePanel");

Ext.define("NOC.inv.inv.plugins.facade.FacadePanel", {
  extend: "Ext.panel.Panel",
  requires: [],
  title: __("Facade"),
  closable: false,
  scrollable: true,
  //
  initComponent: function(){
    var me = this;
    me.facadeViewPanel = Ext.create("Ext.container.Container", {
      scrollable: true,
      layout: "fit",
    });
    Ext.apply(me, {
      items: [me.facadeViewPanel],
    });
    me.callParent();
  },
  //
  preview: function(data){
    var me = this,
      viewQty = data.views.length;
    me.facadeViewPanel.removeAll();
    switch(viewQty){
      case 1:
        me.facadeViewPanel.add(me.makeView(data.views[0]));
        break;
      default:
        me.facadeViewPanel.add([
          {
            xtype: "container",
            padding: 10,
            items: [{
              xtype: "radiogroup",
              fieldLabel: __("Choose view"),
              vertical: false,
              items: Ext.Array.map(data.views, function(view, index){
                return{
                  boxLabel: view.name,
                  name: "chooseView",
                  margin: "0 10 0 0",
                  inputValue: index,
                }
              }),
              listeners: {scope: me, change: me.onChooseView},
            }],
          },
          {
            xtype: "container",
            itemId: "viewPanel",
            layout: "card",
            activeItem: 0,
            items: Ext.Array.map(data.views, function(view){ return{xtype: "container", layout: "fit", items: me.makeView(view)} }), 
          },
        ]);
        me.facadeViewPanel.down("radiogroup").setValue({chooseView: 0});
        break;
    }
  },
  //
  onChooseView: function(field){
    this.down("[itemId=viewPanel]").setActiveItem(field.getValue().chooseView);
  },
  //
  makeView: function(view){
    return[
      {
        xtype: "component",
        html: Ext.String.format("<h2 style='padding: 10px 0 0 10px;'>{0}</h2>", view.name),
      },
      {
        xtype: "image",
        src: view.src,
        title: view.name,
        padding: 5,
      },
    ]
  },
});
