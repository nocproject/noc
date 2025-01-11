//---------------------------------------------------------------------
// inv.inv OPM Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2025 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.opm.OPMPanel");

Ext.define("NOC.inv.inv.plugins.opm.OPMPanel", {
  extend: "Ext.panel.Panel",
  requires: [
    "NOC.inv.inv.plugins.opm.OPMController",
    "NOC.inv.inv.plugins.opm.OPMDiagram",
    "NOC.inv.inv.plugins.opm.OPMRightPanel",
  ],
  title: __("OPM"),
  closable: false,
  controller: "opm",
  layout: "border",
  viewModel: {
    stores: {
      groupsStore: {
        data: [],
      },
      bandsStore: {
        data: [],
      },
    },
    data: {
      isGroupsEmpty: true,
      isBandsEmpty: true,   
      group: undefined,
      band: undefined,
    },  
  },
  tbar: [
    {
      xtype: "combobox",
      fieldLabel: __("Groups"),
      emptyText: __("Select group"),
      valueField: "value",
      displayField: "value",  
      bind: {
        store: "{groupsStore}",
        disabled: "{isGroupsEmpty}",
        value: "{group}",
      },
      editable: false,
      queryMode: "local",
      listeners: {
        select: function(combo, record){
          console.log("Selected:", record.get("value"));
        },
      },
    },
    {
      xtype: "combobox",
      fieldLabel: __("Bands"),
      emptyText: __("Select band"),
      valueField: "value",
      displayField: "value",  
      bind: {
        store: "{bandsStore}",
        disabled: "{isBandsEmpty}",
        value: "{band}",
      },
      editable: false,
      queryMode: "local",
      listeners: {
        select: function(combo, record){
          console.log("Selected:", record.get("value"));
        },
      },
    },
    "->",
    {
      glyph: NOC.glyph.cog,
      tooltip: __("Settings"),
      style: {
        pointerEvents: "all",
      },
      handler: "collapseSettings",
    },
  ],
  items: [
    {
      xtype: "opm.diagram",
      reference: "opmDiagram",
      region: "center",
    },
    {
      xtype: "opm.rightPanel",
      reference: "opmRightPanel",
      region: "east",
      width: "20%",
      split: true,
      collapsed: true,
      hideCollapseTool: true,
      animCollapse: false,
      collapseMode: "mini",
    },
  ],
  remove: function(){
    console.log("Remove all");
  },
  preview: function(data, id){
    var vm = this.getViewModel(),
      bandsStore = vm.getStore("bandsStore"),
      groupsStore = vm.getStore("groupsStore");
      
    bandsStore.loadData(this.mapData(data.bands));
    groupsStore.loadData(this.mapData(data.groups));
    vm.set("isGroupsEmpty", groupsStore.getCount() === 0);
    vm.set("isBandsEmpty", bandsStore.getCount() === 0);
    vm.set("group", groupsStore.getCount() > 0 ? groupsStore.getAt(0).get("value") : undefined);
    vm.set("band", bandsStore.getCount() > 0 ? bandsStore.getAt(0).get("value") : undefined);
  },
  mapData: function(array){
    if(!array){
      return [];
    }
    return Ext.Array.map(array, function(item){
      return {value: item};
    });
  },
});