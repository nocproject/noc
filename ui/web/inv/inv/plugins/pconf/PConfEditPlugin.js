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
  init: function(grid){
    var me = this;
    me.callParent(arguments);
    me.grid = grid;
  },
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
          handler: function(field){
            var value = field.getValue();
            me.context.record.set("value", value);
            me.grid.fireEvent("valuechanged", {name: me.context.record.get("name"), value: value});
          },
        },
        undo: {
          cls: "x-form-trigger fa-undo",
          handler: function(){
            me.editor.setValue(me.originalValue);
          },
        },
      };
 
    if(column.dataIndex === "value" && record.get("read_only") === false){
      if(editorType === "text"){
        editor = new Ext.grid.CellEditor({
          floating: true,
          editorId: editorId,
          field: {
            xtype: "textfield",
            triggers: editorTriggers,
            listeners: {
              specialkey: function(field, e){
                if(e.getKey() == e.ENTER){
                  var value = field.getValue();
                  me.context.record.set("value", value);
                  me.grid.fireEvent("valuechanged", {name: me.context.record.get("name"), value: value});
                }
              },
            },
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
      editor.field.excludeForm = true;
      if(editor.column !== column){
        editor.column = column;
      }
      editors.add(editor);
      editor.ownerCmp = me.grid.ownerGrid;
      if(column.isTreeColumn){
        editor.isForTree = column.isTreeColumn;
        editor.addCls(Ext.baseCSSPrefix + 'tree-cell-editor');
      }
      editor.setGrid(me.grid);
      editor.editingPlugin = me;
      me.editor = editor;
      return editor;
    }            
  },
  
  getEditorType: function(record){
    return record.get("type") === "enum" ? "combo" : "text";
  },
  //
  beforeEdit: function(context){
    this.originalValue = context.value;
  },
});
