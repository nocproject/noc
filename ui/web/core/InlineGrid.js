//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.InlineGrid");

Ext.define("NOC.core.InlineGrid", {
  extend: "Ext.grid.Panel",
  alias: "widget.inlinegrid",
  selType: "rowmodel",
  readOnly: false,
  bbar: {
    xtype: "pagingtoolbar",
    dock: "bottom",
    displayInfo: true,
  },
  defaultListenerScope: true,
  plugins: [
    {
      ptype: "rowediting",
      clicksToEdit: 2,
      listeners: {
        canceledit: "onCancelEdit",
      },
    },
  ],
  tbar: [
    {
      text: __("Add"),
      glyph: NOC.glyph.plus,
      handler: "addHandler",
    },
    {
      text: __("Append"),
      glyph: NOC.glyph.sign_in,
      handler: "appendHandler",
    },
    {
      text: __("Delete"),
      glyph: NOC.glyph.times,
      handler: "deleteHandler",
    },
  ],
  listeners: {
    validateedit: "validator",
  },
  initComponent: function(){
    var me = this;
    this.columns = me.columns;
    this.bbar.store = this.store = me.store;
    this.callParent();
    if(this.readOnly){
      this.down("[dock=top][xtype=toolbar]").hide(true)
    }
  },
  //
  onCancelEdit: function(editor, context){
    if(context.record.phantom){
      context.grid.store.removeAt(context.rowIdx);
    }
  },
  //
  appendHandler: function(){
    var store = this.getStore(),
      position = store.data.length,
      rowEditing = this.plugins[0];
    rowEditing.cancelEdit();
    store.insert(position, {});
    rowEditing.startEdit(position, 0);
  },
  //
  addHandler: function(){
    var rowEditing = this.plugins[0];
    rowEditing.cancelEdit();
    this.getStore().insert(0, {});
    rowEditing.startEdit(0, 0);
  },
  //
  deleteHandler: function(){
    var store = this.getStore(),
      sm = this.getSelectionModel(),
      rowEditing = this.plugins[0];
    rowEditing.cancelEdit();
    store.remove(sm.getSelection());
    if(store.getCount() > 0){
      sm.select(0);
    }
  },
  //
  validator: function(editor, e){
    // @todo: Bring to plugin
    var form = editor.editor.getForm();
    // Process comboboxes
    form.getFields().each(function(field){
      e.record.set(field.name, field.getValue());
      if(Ext.isDefined(field.getLookupData))
        e.record.set(field.name + "__label",
                     field.getLookupData());
    });
  },
});