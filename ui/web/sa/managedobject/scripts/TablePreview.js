//---------------------------------------------------------------------
// TablePreview
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.managedobject.scripts.TablePreview");

Ext.define("NOC.sa.managedobject.scripts.TablePreview", {
  extend: "NOC.sa.managedobject.scripts.ResultPreview",
  requires: [
    "Ext.ux.form.SearchField",
  ],
  columns: [],
  search: false,

  initComponent: function(){
    var me = this,
      fields = [];
    me.searchFields = [];
    // Initialize store
    if(typeof me.fields == "undefined"){
      for(var i in me.columns){
        var c = me.columns[i];
        if(c.dataIndex){
          fields.push({
            name: c.dataIndex,
            type: "auto",
          });
          me.searchFields.push(c.dataIndex);
        }
      }
    } else{
      fields = me.fields;
    }

    me.store = Ext.create("Ext.data.Store", {
      model: null,
      fields: fields,
      data: [],
    });

    me.grid = Ext.create("Ext.grid.Panel", {
      store: me.store,
      features: [{ftype: "grouping"}],
      columns: me.columns,
      viewConfig: {
        enableTextSelection: true,
      },
    });

    Ext.apply(me, {
      items: [me.grid],
    });
    me.callParent();
    me.store.loadData(me.result || []);
  },
  //
  getToolbar: function(){
    var me = this,
      tb = me.callParent();
    if(me.search){
      tb.push("-");
      tb.push(me.getSearchField());
    }
    return tb;
  },
  //
  getSearchField: function(){
    var me = this;
    me.searchField = Ext.create({
      xtype: "searchfield",
      name: "search_field",
      hideLabel: true,
      scope: me,
      handler: me.onSearch,
    });
    return me.searchField;
  },
  //
  onSearch: function(value){
    var me = this;
    value = value.toLowerCase();
    me.store.clearFilter(true);
    me.store.filterBy(function(record){
      for(var i in me.searchFields){
        var n = me.searchFields[i];
        if(String(record.get(n)).toLowerCase().indexOf(value) !== -1){
          return true;
        }
      }
      return false;
    });
  },
});
