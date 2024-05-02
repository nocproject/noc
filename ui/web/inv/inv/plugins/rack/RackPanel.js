//---------------------------------------------------------------------
// inv.inv.plugins.inventory InventoryPanel
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.rack.RackPanel");

Ext.define("NOC.inv.inv.plugins.rack.RackPanel", {
  extend: "NOC.core.ApplicationPanel",
  requires: ["NOC.core.Rack", "NOC.inv.inv.plugins.rack.RackLoadModel"],
  app: null,
  scrollable: true,
  title: __("Rack"),
  layout: "border",

  initComponent: function(){
    var me = this;

    me.reloadButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.refresh,
      scope: me,
      tooltip: __("Reload"),
      handler: me.onReload,
    });

    me.zoomButton = Ext.create("Ext.form.ComboBox", {
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
      listeners: {
        scope: me,
        select: me.onZoom,
      },
    });

    me.sideFrontButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.hand_o_right,
      text: __("Front"),
      scope: me,
      toggleGroup: "side",
      pressed: true,
      handler: me.onReload,
    });

    me.sideRearButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.hand_o_left,
      text: __("Rear"),
      scope: me,
      toggleGroup: "side",
      handler: me.onReload,
    });

    me.segmentedButton = Ext.create("Ext.button.Segmented", {
      items: [me.sideFrontButton, me.sideRearButton],
    });

    me.editLoadButton = Ext.create("Ext.button.Button", {
      text: __("Edit"),
      glyph: NOC.glyph.edit,
      scope: me,
      handler: me.onEdit,
      enableToggle: true,
    });

    me.drawPanel = Ext.create("Ext.draw.Container", {
      scrollable: true,
      plugins: ["spriteevents"],
      listeners: {
        spriteclick: function(sprite){
          if(sprite.sprite.managed_object_id){
            window.open(
              "/api/card/view/managedobject/" + sprite.sprite.managed_object_id + "/",
            );
          }
        },
      },
    });

    me.rackViewPanel = Ext.create("Ext.container.Container", {
      scrollable: true,
      region: "center",
      items: me.drawPanel,
    });

    me.rackLoadStore = Ext.create("Ext.data.Store", {
      model: "NOC.inv.inv.plugins.rack.RackLoadModel",
    });

    me.rackLoadPanel = Ext.create("Ext.grid.Panel", {
      store: me.rackLoadStore,
      region: "east",
      width: 500,
      hidden: true,
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
          clicksToEdit: 2,
        }),
      ],
      listeners: {
        scope: me,
        validateedit: Ext.bind(me.onCellValidateEdit, me),
        edit: Ext.bind(me.onCellEdit, me),
      },
    });

    Ext.apply(me, {
      items: [me.rackViewPanel, me.rackLoadPanel],
      dockedItems: [
        {
          xtype: "toolbar",
          dock: "top",
          items: [me.reloadButton, "-", me.segmentedButton, me.zoomButton, "-", me.editLoadButton],
        },
      ],
    });

    me.callParent();
  },
  //
  preview: function(data){
    var me = this,
      {sprites, height} = NOC.core.Rack.getRack(me, 5, 5, data.rack, data.content, me.getSide());
    me.drawPanelHeight = height;
    me.zoomButton.setValue(1.0);
    me.drawPanel.getSurface().removeAll();
    me.drawPanel.getSurface().add(sprites);
    me.drawPanel.renderFrame();
    me.drawPanel.setHeight(height);
    me.currentId = data.id;
    me.rackLoadStore.loadData(data.load);
  },
  //
  getSide: function(){
    var me = this;
    return me.sideRearButton.pressed ? "r" : "f";
  },
  //
  onReload: function(){
    var me = this;
    Ext.Ajax.request({
      url: "/inv/inv/" + me.currentId + "/plugin/rack/",
      method: "GET",
      scope: me,
      success: function(response){
        me.preview(Ext.decode(response.responseText));
      },
      failure: function(){
        NOC.error(__("Failed to get data"));
      },
    });
  },
  //
  onEdit: function(){
    var me = this;

    if(me.editLoadButton.pressed){
      me.rackLoadPanel.show();
    } else{
      me.rackLoadPanel.hide();
    }
  },
  onCellValidateEdit: function(){
    return true;
  },
  //
  onCellEdit: function(editor, e){
    var me = this;
    if(e.field === "position_front"){
      e.record.set("position_rear", 0);
    }
    if(e.field === "position_rear"){
      e.record.set("position_front", 0);
    }
    // Submit
    Ext.Ajax.request({
      url: "/inv/inv/" + me.currentId + "/plugin/rack/rackload/",
      method: "POST",
      scope: me,
      jsonData: {
        cid: e.record.get("id"),
        position_front: e.record.get("position_front"),
        position_rear: e.record.get("position_rear"),
        shift: e.record.get("shift"),
      },
      loadMask: me,
      success: function(){
        me.onReload();
      },
      failure: function(){
        NOC.error(__("Failed to save"));
      },
    });
  },
  //
  onObjectSelect: function(objectId){
    var me = this;
    me.app.showObject(objectId);
  },
  //
  onZoom: function(field){
    var me = this,
      zoom = field.getValue();
    
    Ext.each(me.drawPanel.getSurface().getItems(), function(sprite){
      sprite.setTransform([zoom, 0, 0, zoom, 0, 0]);
    });
    me.drawPanel.setHeight(parseInt(me.drawPanelHeight * zoom));
    me.drawPanel.renderFrame();
  },
});
