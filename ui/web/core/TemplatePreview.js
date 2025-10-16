//---------------------------------------------------------------------
// NOC.core.TemplatePreview
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.TemplatePreview");

Ext.define("NOC.core.TemplatePreview", {
  extend: "Ext.panel.Panel",
  layout: "fit",
  app: null,
  template: null,
  previewName: null,
  onCloseItem: null,

  initComponent: function(){
    var me = this;

    Ext.apply(me, {
      dockedItems: [{
        xtype: "toolbar",
        dock: "top",
        items: [
          {
            itemId: "close",
            text: __("Close"),
            glyph: NOC.glyph.arrow_left,
            scope: me,
            handler: me.onClose,
          },
        ],
      }],
      items: [{
        xtype: "container",
        autoScroll: true,
        padding: 4,
      }],
    });
    me.callParent();
  },
  //
  preview: function(record, extra){
    var me = this,
      context = {};
    Ext.apply(context, record.data);
    if(extra){
      Ext.apply(context, extra);
    }
    me.setTitle(me.previewName.apply(context));
    me.items.first().update(me.template.apply(context));
  },
  //
  onClose: function(){
    var me = this,
      idx;

    if(me.onCloseItem === null){
      idx = me.app.ITEM_GRID;
    } else{
      if(Ext.isString(me.onCloseItem)){
        idx = me.app[me.onCloseItem];
      } else{
        idx = me.onCloseItem;
      }
    }
    me.app.showItem(idx);
  },
});
