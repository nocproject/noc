//---------------------------------------------------------------------
// inv.inv.plugins.rack RackPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.rack.RackPanel");

Ext.define("NOC.inv.inv.plugins.rack.RackPanel", {
  extend: "NOC.core.ApplicationPanel",
  requires: [
    "NOC.inv.inv.plugins.rack.RackLoadModel",
    "NOC.inv.inv.plugins.rack.Controller",
  ],
  app: null,
  scrollable: true,
  title: __("Rack"),
  layout: "border",
  controller: "rack",
  viewModel: {
    stores: {
      gridStore: {
        model: "NOC.inv.inv.plugins.rack.RackLoadModel",
        listeners: {
          datachanged: "onDataChanged",
        },
      },
    },
    data: {
      currentId: null,
      side: "front",
      edit: false,
      totalCount: 0,
    },
    formulas: {
      isFrontPressed: function(get){
        return get("side") === "front";
      },
      isRearPressed: function(get){
        return get("side") === "rear";
      },
    },

  },
  items: [
    {
      xtype: "container",
      itemId: "viewPanel",
      layout: "auto",
      scrollable: true,
      region: "center",
    },
    {
      xtype: "grid",
      bind: {
        store: "{gridStore}",
        hidden: "{!edit}",
      },
      region: "east",
      width: 500,
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 100,
        },
        {
          text: __("Model"),
          dataIndex: "model",
          width: 200,
        },
        {
          text: __("Units"),
          dataIndex: "units",
          width: 50,
        },
        {
          text: __("Front"),
          tooltip: __("Position Front"),
          dataIndex: "position_front",
          width: 50,
          editor: {
            xtype: "numberfield",
            minWidth: 75,
            minValue: 0,
          },
          renderer: function(v){
            if(v === 0){
              return "-";
            } else{
              return v.toString();
            }
          },
        },
        {
          text: __("Rear"),
          tooltip: __("Position Rear"),
          dataIndex: "position_rear",
          width: 50,
          editor: {
            xtype: "numberfield",
            minWidth: 75,
            minValue: 0,
          },
          renderer: function(v){
            if(v === 0){
              return "-";
            } else{
              return v.toString();
            }
          },
        },
        {
          text: __("Shift"),
          dataIndex: "shift",
          width: 70,
          editor: {
            xtype: "combobox",
            store: [
              [0, "-"],
              [1, "1"],
              [2, "2"],
            ],
          },
          renderer: function(v){
            if(v === 0){
              return "-";
            } else{
              return v.toString();
            }
          },
        },
      ],
      selType: "cellmodel",
      plugins: [
        Ext.create("Ext.grid.plugin.CellEditing", {
          clicksToEdit: 1,
        }),
      ],
      listeners: {
        validateedit: "onCellValidateEdit",
        edit: "onCellEdit",
      },
    },
  ],
  tbar: [
    {
      glyph: NOC.glyph.refresh,
      tooltip: __("Reload"),
      handler: "onReload",
    },
    "-",
    {
      xtype: "segmentedbutton",
      items: [
        {
          glyph: NOC.glyph.hand_o_right,
          text: __("Front"),
          toggleGroup: "side",
          bind: {
            pressed: "{isFrontPressed}",
          },
          handler: "onFrontPressed",
        },
        {
          glyph: NOC.glyph.hand_o_left,
          text: __("Rear"),
          toggleGroup: "side",
          bind: {
            pressed: "{isRearPressed}",
          },
          handler: "onRearPressed", 
        },
      ],
    },
    "-",
    {
      xtype: "combo",
      itemId: "zoomButton",
      store: [
        [0.25, "25%"],
        [0.5, "50%"],
        [0.75, "75%"],
        [1.0, "100%"],
        [1.25, "125%"],
        [1.5, "150%"],
        [2.0, "200%"],
        [3.0, "300%"],
        [4.0, "400%"],
      ],
      width: 100,
      value: 1.0,
      valueField: "zoom",
      displayField: "label",
      editable: false,
      listeners: {
        select: "onZoom",
      },
    },
    {
      text: __("Edit"),
      glyph: NOC.glyph.edit,
      enableToggle: true,
      bind: {
        pressed: "{edit}",
      },
      handler: function(){
        var vm = this.up("panel").getViewModel();
        vm.set("edit", !vm.get("edit"));
      },
    },
  ],
  preview: function(data){
    var me = this,
      padding = 5,
      viewPanel = me.down("#viewPanel"),
      zoomButton = me.down("#zoomButton"),
      vm = me.getViewModel(),
      url = "/inv/inv/" + data.id + "/plugin/rack/" + vm.get("side") + ".svg";
    vm.get("gridStore").loadData(data.load);
    vm.set("currentId", data.id);
    viewPanel.removeAll();
    viewPanel.add({
      xtype: "container",
      itemId: "image",
      html: "<object id='svg-object' data='" + url + "' type='image/svg+xml'></object>",
      padding: padding,
      listeners: {
        afterrender: "onAfterRender",
      },
    });
    zoomButton.setValue(1.0);
    viewPanel.down("#image").getEl().dom.querySelector("object").style.height = viewPanel.getHeight() - padding * 2 + "px";
  },
});
