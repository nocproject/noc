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
  mixins: [
    "NOC.inv.inv.plugins.Mixins",
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
      currentId: undefined,
      icon: "<i class='fa fa-fw' style='padding-left:4px;width:16px;'></i>",
    },  
  },
  timer: undefined,
  // listeners: {
  //   activate: "onActivate",
  // },
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
        select: "onComboboxSelect",
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
        select: "onComboboxSelect", 
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
    {
      xtype: "tbtext",
      bind: {
        html: "{icon}",
      },
    },
  ],
  items: [
    {
      xtype: "opm.diagram",
      reference: "opmDiagram",
      region: "center",
      border: true,
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
      
    this.observer = this.setObservable(this);
    bandsStore.loadData(this.mapData(data.bands));
    groupsStore.loadData(this.mapData(data.groups));
    vm.set("isGroupsEmpty", groupsStore.getCount() === 0);
    vm.set("isBandsEmpty", bandsStore.getCount() === 0);
    vm.set("currentId", id);
    vm.set("group", groupsStore.getCount() > 0 ? groupsStore.getAt(0).get("value") : undefined);
    vm.set("band", bandsStore.getCount() > 0 ? bandsStore.getAt(0).get("value") : undefined);
    this.timer = Ext.TaskManager.start({
      run: this.reloadTask,
      interval: 3000,
      args: [this.getController().onReload],
      scope: this,
    });
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