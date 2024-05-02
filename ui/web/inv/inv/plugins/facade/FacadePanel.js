//---------------------------------------------------------------------
// inv.inv Facade panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.facade.FacadePanel");

Ext.define("NOC.inv.inv.plugins.facade.FacadePanel", {
  extend: "Ext.panel.Panel",
  requires: [],
  title: __("Facade"),
  closable: false,
  scrollable: true,
  //
  initComponent: function(){
    var me = this;
    me.reloadButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.refresh,
      scope: me,
      tooltip: __("Reload"),
      handler: me.onReload,
    });

    me.sideFrontButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.hand_o_right,
      text: __("Front"),
      scope: me,
      toggleGroup: "side",
      pressed: true,
      handler: function(){
        me.viewCard.setActiveItem(0);
      },
    });

    me.sideRearButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.hand_o_left,
      text: __("Rear"),
      scope: me,
      toggleGroup: "side",
      handler: function(){
        me.viewCard.setActiveItem(1);
      },
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

    me.segmentedButton = Ext.create("Ext.button.Segmented", {
      items: [me.sideFrontButton, me.sideRearButton],
    });

    me.viewCard = Ext.create("Ext.container.Container", {
      xtype: "container",
      layout: "card",
      activeItem: 0,
    });

    me.facadeViewPanel = Ext.create("Ext.container.Container", {
      scrollable: true,
      layout: "fit",
      items: [me.viewCard],
    });

    Ext.apply(me, {
      items: [me.facadeViewPanel],
      dockedItems: [
        {
          xtype: "toolbar",
          dock: "top",
          items: [me.reloadButton, "-", me.segmentedButton, me.zoomButton],
        },
      ],
    });
    me.callParent();
  },
  //
  preview: function(data){
    var me = this;
    me.currentId = data.id;
    // Add views
    me.viewCard.removeAll();
    me.viewCard.add(
      Ext.Array.map(data.views, function(view){
        return {
          xtype: "container",
          layout: "fit",
          items: [
            {
              xtype: "image",
              src: view.src,
              title: view.name,
              padding: 5,
            },
          ],
        };
      }),
    );
    // Disable rear button if necessary
    me.sideRearButton.setDisabled(data.views.length < 2);
    // Press front button
    me.sideFrontButton.setPressed(true);
  },
  //
  onReload: function(){
    var me = this;
    Ext.Ajax.request({
      url: "/inv/inv/" + me.currentId + "/plugin/facade/",
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
  onZoom: function(combo){
    console.log("Zoom to", combo.getValue());
  },
});
