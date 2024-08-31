//---------------------------------------------------------------------
// inv.inv PConfigEditPlugin
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.pconf.PConfEditPlugin");

Ext.define("NOC.inv.inv.plugins.pconf.PConfEditPlugin", {
  extend: "Ext.grid.plugin.CellEditing",
  alias: "plugin.valueedit",

  //
  getEditor: function(record, column){
    var me = this,
      editors = me.editors,
      editorId = column.getItemId(),
      editor = editors.getByKey(editorId),
      editorType = me.getEditorType(record),
      editorTriggers = {
        save: {
          cls: "x-form-trigger fa-save",
          handler: function(){
            console.log("Save");
          },
        },
        undo: {
          cls: "x-form-trigger fa-undo",
          handler: function(){
            console.log("Undo");
          },
        },
      };
 
    if(column.dataIndex === "value"){
      if(editorType === "text"){
        editor = new Ext.grid.CellEditor({
          floating: true,
          editorId: editorId,
          field: {
            xtype: "textfield",
            triggers: editorTriggers,
          },
        });
      } else if(editorType === "combo"){
        editor = new Ext.grid.CellEditor({
          floating: true,
          editorId: editorId,
          field: {
            xtype: "combobox",
            triggers: editorTriggers,
            store: {
              fields: ["id", "label"],
              data: record.get("options") || [],
            },
            valueField: "id",
            displayField: "label",
            queryMode: "local",
          },
        });
      }
    }            
    editor.field.excludeForm = true;
    if(editor.column !== column){
      editor.column = column;
      editor.on({
        scope: me,
        complete: me.onEditComplete,
        canceledit: me.cancelEdit,
      });
      column.on('removed', me.onColumnRemoved, me);
    }
    editors.add(editor);
    editor.ownerCmp = me.grid.ownerGrid;
    if(column.isTreeColumn){
      editor.isForTree = column.isTreeColumn;
      editor.addCls(Ext.baseCSSPrefix + 'tree-cell-editor');
    }
    editor.setGrid(me.grid);
    editor.editingPlugin = me;
    return editor;
  },
  //
  getEditorType: function(record){
    return record.get("type") === "enum" ? "combo" : "text";
  },
});
