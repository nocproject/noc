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
  disabledTooltip: __("This grid is currently disabled. Fill all required fields and press 'Apply' button to enable it."),
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
        validateedit: "validator",
        edit: "onEdit",
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
  initComponent: function(){
    var me = this;
    this.columns = me.columns;
    this.bbar.store = this.store = me.store;
    me.on({
      afterrender: "setupDisabledTooltip",
      disable: "onDisable",
      enable: "onEnable",
    });
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
    this.storeSync(store, __("deleted"), __("deleting"));
  },
  //
  validator: function(editor, context){
    var form = editor.editor.getForm();
    // Process comboboxes
    form.getFields().each(function(field){
      context.record.set(field.name, field.getValue());
      if(Ext.isDefined(field.getLookupData))
        context.record.set(field.name + "__label",
                           field.getLookupData());
    });
  },
  //
  onEdit: function(editor, context){
    this.storeSync(context.grid.getStore(), __("saved"), __("saving"));
  },
  //
  storeSync: function(store, success, failure){
    store.sync({
      success: function(){
        NOC.info(__("Changes") + " " + success);
      },
      failure: function(){
        NOC.error(__("Error" + " " + failure + " " + __("changes")));
      },
    });
  },
  //
  setupDisabledTooltip: function(){
    if(this.disabled){
      this.addDisabledTooltip();
    }
  },
  //
  addDisabledTooltip: function(){
    var me = this;
    if(me.disabledTip){
      me.disabledTip.destroy();
      me.disabledTip = null;
    }
    //
    me.disabledTip = Ext.create("Ext.tip.ToolTip", {
      target: me.el,
      html: me.disabledTooltip,
      showDelay: 100,
      hideDelay: 200,
      dismissDelay: 10000, // 10 sec
      trackMouse: true,
    });
  },
  //
  removeDisabledTooltip: function(){
    if(this.disabledTip){
      this.disabledTip.destroy();
      this.disabledTip = null;
    }
  },
  //
  onDisable: function(){
    this.addDisabledTooltip();
  },  
  //
  onEnable: function(){
    this.removeDisabledTooltip();
  },
});