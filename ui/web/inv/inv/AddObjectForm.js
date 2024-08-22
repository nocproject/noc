//---------------------------------------------------------------------
// inv.inv AddObject form
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.AddObjectForm");

Ext.define("NOC.inv.inv.AddObjectForm", {
  extend: "Ext.panel.Panel",
  requires: ["NOC.inv.objectmodel.LookupField"],
  app: null,
  padding: 4,
  layout: "fit",
  defaultListenerScope: true,
  title: __("Create new top-level object"),
  dockedItems: [
    {
      xtype: "toolbar",
      dock: "top",
      padding: "4 4 4 0",
      items: [
        {
          text: __("Save"),
          glyph: NOC.glyph.save,
          handler: "onPressAdd",
        },
        {
          text: __("Close"),
          glyph: NOC.glyph.arrow_left,
          handler: "onPressClose",
        },
        "|",
        {
          text: __("Clear"),
          tooltip: __("Clear all rows"),
          glyph: NOC.glyph.minus_circle,
          handler: "onClearAll",
        },
        {
          text: __("Add row"),
          glyph: NOC.glyph.plus,
          handler: "onAddRow",
        },
      ],
    },
  ],
  items: [
    {
      xtype: "grid",
      scrollable: true,
      store: {
        fields: [
          {name: "name", type: "string", allowBlank: false},
          {name: "model", type: "string", allowBlank: false},
          {name: "serial", type: "string", allowBlank: true},
        ],
        data: [{}],
      },
      plugins: {
        ptype: "cellediting",
        clicksToEdit: 1,
      },
      columns: [
        {
          xtype: "actioncolumn",
          width: 50,
          items: [
            {
              iconCls: "x-fa fa-times",
              tooltip: __("Remove"),
              handler: function(grid, rowIndex){
                grid.getStore().removeAt(rowIndex);
              },
            },
            {
              iconCls: "x-fa fa-clone",
              tooltip: __("Clone"),
              isDisabled: function(view, rowIndex, colIndex, item, record){
                return Ext.isEmpty(record.get("model")) || Ext.isEmpty(record.get("name"));
              },
              handler: function(grid, rowIndex){
                var newName,
                  toRemove = [],
                  maxNumber = 0,
                  store = grid.getStore(),
                  record = store.getAt(rowIndex).copy(),
                  data = Ext.apply({}, record.getData()),
                  name = record.get("name"),
                  baseName = name.replace(/(\d+)$/, "");
                
                store.each(function(rec){
                  if(rec.get("name").indexOf(baseName) === 0){
                    var num = parseInt(rec.get("name").replace(baseName, ""), 10);
                    if(num > 0){
                      maxNumber = Math.max(maxNumber, num);
                    }
                  }
                });
                newName = maxNumber ? baseName + (maxNumber + 1) : baseName + "2";
    
                var newRecord = Ext.create(record.self, {
                  name: newName,
                  model: data.model,
                  serial: "",
                });

                store.each(function(rec){
                  if(Ext.isEmpty(rec.get("name")) && Ext.isEmpty(rec.get("model"))){
                    toRemove.push(rec);
                  }
                });
                
                store.remove(toRemove);
                store.add(newRecord);
                store.add({});
              },
            },
          ],
        },
        {
          text: __("Name"),
          dataIndex: "name",
          editor: "textfield",
          flex: 1,
        },
        { 
          text: __("Model"), 
          dataIndex: "model", 
          renderer: function(value, metaData, record, rowIndex, colIndex, store, view){
            var column = view.getGridColumns()[colIndex],
              editor = column.getEditor();
            if(editor && editor.xtype === "inv.objectmodel.LookupField"){
              var rec = editor.findRecordByValue(value);
              return rec ? rec.get(editor.displayField) : value;
            }
            return "";
          }, 
          editor: {
            xtype: "inv.objectmodel.LookupField",
            editable: true,
          },
          flex: 1, 
        },
        {
          text: __("Serial"),
          dataIndex: "serial",
          editor: "textfield",
          flex: 1,
        },
      ],
      listeners: {
        edit: function(editor, context){
          var store = context.grid.getStore(),
            lastRecord = store.last();
    
          if(context.record === lastRecord &&
                (!Ext.isEmpty(lastRecord.get("name")) && !Ext.isEmpty(lastRecord.get("model")))){
            store.add({});
          }
        },
      },
    },
  ],
  //
  onPressClose: function(){
    var me = this;
    me.app.showItem(me.app.ITEM_MAIN);
  },
  //
  onPressAdd: function(){
    var me = this,
      items = this.down("grid").getStore().getData().items,
      data = Ext.Array.map(
        Ext.Array.filter(items, function(record){
          return !Ext.isEmpty(record.get("name")) && !Ext.isEmpty(record.get("model"));
        }),
        function(record){
          var item = {
            name: record.get("name"),
            model: record.get("model"),
          }
          if(record.get("serial")){
            item.serial = record.get("serial");
          } 
          return item; 
        });
    Ext.Ajax.request({
      url: "/inv/inv/add/",
      method: "POST",
      jsonData: {
        items: data,
        container: me.groupContainer ? me.groupContainer.get("id") : null,
      },
      scope: me,
      success: function(response){
        var status = Ext.decode(response.responseText);
        me.app.showItem(me.app.ITEM_MAIN);
        if(status.status){
          NOC.info(__("Saved"));
          if(me.groupContainer){
            me.app.store.reload({node: me.groupContainer});
            me.groupContainer.expand();
            me.app.setHistoryHash(me.groupContainer);
          }
        } else{
          NOC.error(__("Failed to save"));
        }
      },
      failure: function(){
        NOC.error(__("Failed to save"));
      },
    });
  },
  //
  setContainer: function(container){
    var me = this;
    me.groupContainer = container;
    me.setTitle(__("Add object to ") + (container ? container.getPath("name") : __("Root")));
  },
  //
  onAddRow: function(){
    var me = this,
      store = me.down("grid").getStore();
    store.add({});
  },
  //
  onClearAll: function(){
    var me = this;
    Ext.Msg.confirm(
      __("Confirmation"),
      __("Are you sure you want to delete all rows?"),
      function(btn){
        if(btn === "yes"){
          var store = me.down("grid").getStore();
          store.removeAll();
          store.add({});
        }
      },
    );
  },
});
