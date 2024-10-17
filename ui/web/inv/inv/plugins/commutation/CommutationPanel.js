//---------------------------------------------------------------------
// inv.inv Commutation Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.commutation.CommutationPanel");

Ext.define("NOC.inv.inv.plugins.commutation.CommutationPanel", {
  extend: "NOC.inv.inv.plugins.VizSchemePluginAbstract",
  title: __("Commutation"),
  itemId: "commutationPanel",
  gridColumns: [
    {
      text: __("Local Object"),
      dataIndex: "local_object",
      renderer: NOC.render.Lookup("local_object"),
      flex: 1,
    },
    {
      text: __("Local Name"),
      dataIndex: "local_name",
      width: 100,
    },
    {
      text: __("Remote Object"),
      dataIndex: "remote_object",
      flex: 1,
      renderer: NOC.render.Lookup("remote_object"),
    },
    {
      text: __("Remote Name"),
      dataIndex: "remote_name",
      width: 100,
    },
  ],
  initComponent: function(){
    var tbarItems = Ext.clone(this.tbar),
      filterCombo = {
        xtype: "combobox",
        itemId: "filterCombo",
        editable: false,
        valueField: "id",
        bind: {
          disabled: "{!showDetails}",
        },
        width: 300,
        triggers: {
          clear: {
            cls: "x-form-clear-trigger",
            weight: -1,
            hidden: true,
            handler: function(combo){
              var grid = combo.up("panel").down("grid");
              combo.clearValue();
              combo.getTrigger("clear").hide();
              grid.getStore().clearFilter();
            },
          },
        },
        listConfig: {
          minWidth: 400,
        },
        listeners: {
          select: function(combo){
            var grid = combo.up("panel").down("grid"),
              store = grid.getStore(),
              value = combo.getValue();
            store.clearFilter();
            store.filterBy(function(record){
              return record.get("local_object") === value || record.get("remote_object") === value;
            });
          },
          change: function(combo){
            var grid = combo.up("panel").down("grid"),
              value = combo.getValue();
            if(value === ""){
              grid.getStore().clearFilter();
              combo.getTrigger("clear").hide();
            } else{
              combo.getTrigger("clear").show();
            }
          },
          afterrender: function(combo){
            if(!combo.getValue()){
              combo.getTrigger("clear").hide();
            }
          },
        },
      };
    tbarItems.splice(tbarItems.length - 2, 0, filterCombo);
    this.tbar = tbarItems;
    this.callParent(arguments);
  },
  // Override
  preview: function(response, objectId){
    this.callParent([response, objectId]);
    this.applyFilter(response.data || []);
  },
  // Override
  showHideDetails: function(button, pressed){
    var me = this,
      filterCombo = me.up().down("#filterCombo");

    if(filterCombo){
      filterCombo.setDisabled(!pressed);
    }
    me.callParent([button, pressed])},
  //
  applyFilter: function(records){
    var me = this,
      filterCombo = me.down("#filterCombo"),
      comboData = me.joinForCombo(records),
      grid = me.down("grid");
    grid.getStore().clearFilter();
    filterCombo.setStore(Ext.create("Ext.data.Store", {
      fields: ["id", "text"],
      data: comboData,
    }));
    filterCombo.setValue("");
    filterCombo.getTrigger("clear").hide();    
  },
  //
  joinForCombo: function(data){
    var result = new Set();
    data.forEach(function(item){
      result.add(JSON.stringify({id: item.local_object, text: item.local_object__label}));
      result.add(JSON.stringify({id: item.remote_object, text: item.remote_object__label}));
    });
    return Array.from(result).map(item => JSON.parse(item));
  },
});
