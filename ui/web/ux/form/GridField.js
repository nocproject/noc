//---------------------------------------------------
// Ext.ux.form.GridField
//     ExtJS4 form field
//     Embedded grid
//---------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------
Ext.define("Ext.ux.form.GridField", {
  extend: "Ext.form.FieldContainer",
  mixins: {
    field: "Ext.form.field.Field",
  },
  alias: "widget.gridfield",
  columns: [],
  toolbar: null,

  initComponent: function(){
    var me = this,
      toolbar;

    me.fields = me.columns.map(function(v){
      return v.dataIndex;
    });

    // Add ghost __label fields
    me.fields = me.fields.concat(me.columns.map(function(v){
      return {
        name: v.dataIndex + "__label",
        persist: false,
      }
    }));

    me.store = Ext.create("Ext.data.Store", {
      fields: me.fields,
      data: [],
    });

    me.insertButton = Ext.create("Ext.button.Button", {
      text: __("Insert"),
      glyph: NOC.glyph.plus,
      scope: me,
      handler: me.onAddRecord,
    });

    me.appendButton = Ext.create("Ext.button.Button", {
      text: __("Append"),
      glyph: NOC.glyph.sign_in,
      scope: me,
      handler: Ext.pass(me.onAddRecord, true),
    });

    me.deleteButton = Ext.create("Ext.button.Button", {
      text: __("Delete"),
      glyph: NOC.glyph.minus,
      disabled: true,
      scope: me,
      handler: me.onDeleteRecord,
    });

    me.cloneButton = Ext.create("Ext.button.Button", {
      text: __("Clone"),
      glyph: NOC.glyph.copy,
      disabled: true,
      scope: me,
      handler: me.onCloneRecord,
    });

    // Build toolbar
    toolbar = [
      me.insertButton,
      me.appendButton,
      me.deleteButton,
      "-",
      me.cloneButton,
    ];
    if(me.toolbar){
      toolbar.push("-");
      toolbar = toolbar.concat(me.toolbar);
    }

    me.grid = Ext.create("Ext.grid.Panel", {
      layout: "fit",
      store: me.store,
      columns: me.columns,
      plugins: [
        Ext.create("Ext.grid.plugin.CellEditing", {
          clicksToEdit: 2,
          listeners: {
            scope: me,
            edit: me.onCellEdit,
            beforeedit: me.onBeforeEdit,
          },
        }),
      ],
      dockedItems: [
        {
          xtype: "toolbar",
          dock: "top",
          items: toolbar,
        },
      ],
      listeners: {
        scope: me,
        select: me.onSelect,
      },
      viewConfig: {
        plugins: {
          ptype: "gridviewdragdrop",
          dragtext: __("Drag and drop to reorganize"),
        },
        getRowClass: function(record){
          var pfix = Ext.baseCSSPrefix,
            disabledClass = pfix + "item-disabled " + pfix + "btn-disabled " + pfix + "btn-plain-toolbar-small";
          return record.get("is_persist") ? disabledClass : "";
        },
      },
    });

    Ext.apply(me, {
      items: [
        me.grid,
      ],
    });
    me.currentSelection = undefined;
    me.callParent();
  },
  //
  getSubmitData: function(){
    var me = this,
      data = null;
    if(!me.disabled && me.submitValue){
      data = {};
      data[me.getName()] = me.getValue();
    }
    return data;
  },
  //
  getModelData: function(includeEmptyText, isSubmitting){
    var me = this,
      records = [];

    me.store.each(function(r){
      var data = {};

      if(r.get("is_persist")){
        return true;
      }
      if(!me.disabled && (me.submitValue || !isSubmitting)){
        data = {};
        for(var index = 0; index < me.columns.length; index++){
          var field = me.grid.columns[index],
            dataIndex = me.columns[index].dataIndex;

          if(Ext.isObject(field) && Ext.isDefined(field.persist) && field.persist === false){
            return true;
          }

          if(Ext.isFunction(field.getEditor) && field.getEditor() && Ext.isFunction(field.getEditor().getArrayValues)){
            data[dataIndex] = field.getEditor().getArrayValues(r.get(dataIndex));
          } else{
            data[dataIndex] = r.get(dataIndex);
          }
        }
      }
      records.push(data);
    });
    return records;
  },
  //
  getValue: function(){
    var me = this,
      records = [];
    me.store.each(function(r){
      var d = {};
      if(r.get("is_persist")){
        return true;
      }
      Ext.each(me.fields, function(f){
        if(Ext.isObject(f) && Ext.isDefined(f.persist) && f.persist === false){
          return true;
        }
        d[f] = r.get(f);
      });
      records.push(d);
    });
    return records;
  },
  //
  setValue: function(v){
    var me = this;
    if(v === undefined || v === ""){
      v = [];
    } else{
      v = v || [];
    }
    me.store.loadData(v);
    return me.mixins.field.setValue.call(me, v);
  },
  //
  onSelect: function(grid, record, index){
    var me = this;
    me.currentSelection = index;
    me.deleteButton.setDisabled(true);
    me.cloneButton.setDisabled(true);
    if(!record.get("is_persist")){
      me.deleteButton.setDisabled(false);
      me.cloneButton.setDisabled(false);
    }
  },
  //
  onAddRecord: function(self, evt, toEnd){
    var me = this,
      rowEditing = me.grid.plugins[0],
      position = 0;
    if(toEnd){
      position = me.grid.store.data.length;
    }
    rowEditing.cancelEdit();
    me.grid.store.insert(position, {});
    rowEditing.startEdit(position, 0);
  },
  //
  onDeleteRecord: function(){
    var me = this,
      sm = me.grid.getSelectionModel(),
      rowEditing = me.grid.plugins[0];
    rowEditing.cancelEdit();
    me.grid.store.remove(sm.getSelection());
    if(me.grid.store.getCount() > 0){
      sm.select(0);
    } else{
      me.deleteButton.setDisabled(true);
      me.cloneButton.setDisabled(true);
    }
    me.fireEvent("delete");
  },
  //
  onCloneRecord: function(){
    var me = this,
      sm = me.grid.getSelectionModel(),
      sel = sm.getLastSelected(),
      rowEditing = me.grid.plugins[0],
      newRecord;
    if(!sel){
      return;
    }
    rowEditing.cancelEdit();
    newRecord = sel.copy();
    delete newRecord.data.id;
    newRecord = me.store.createModel(newRecord.data);
    me.fireEvent("clone", newRecord);
    me.currentSelection += 1;
    me.grid.store.insert(me.currentSelection, newRecord);
    sm.select(me.currentSelection);
  },
  //
  onCellEdit: function(editor, context){
    var ed = context.grid.columns[context.colIdx].getEditor(),
      field = context.grid.columns[context.colIdx].field;
    if(ed.rawValue){
      context.record.set(context.field + "__label", ed.rawValue);
    }
    if(field.xtype === "labelfield"){
      context.value = field.valueCollection.items;
    }
  },
  //
  onBeforeEdit: function(editor, context){
    context.cancel = context.record.get("is_persist");
  },
});
