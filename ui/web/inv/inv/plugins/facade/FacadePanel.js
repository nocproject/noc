//---------------------------------------------------------------------
// inv.inv Facade panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.facade.FacadePanel");

Ext.define("NOC.inv.inv.plugins.facade.FacadePanel", {
  extend: "Ext.panel.Panel",
  requires: [
    "NOC.inv.inv.plugins.Zoom",
  ],
  mixins: [
    "NOC.core.mixins.SVGInteraction",
    "NOC.inv.inv.plugins.Mixins",
  ],
  itemId: "facadePanel",
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
      value: "front",
      handler: function(){
        me.preview(me.data);
      },
    });

    me.sideRearButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.hand_o_left,
      text: __("Rear"),
      scope: me,
      toggleGroup: "side",
      value: "rear",
      handler: function(){
        me.preview(me.data);
      },
    });

    me.zoomButton = Ext.create("NOC.inv.inv.plugins.Zoom", {
      itemId: "zoomControl",
      appPanel: me.itemId,
    });

    me.downloadButton = Ext.create("Ext.button.Button", {
      tooltip: __("Download image as SVG"),
      glyph: NOC.glyph.download,
      scope: me,
      handler: me.onDownloadSVG,
    });

    me.segmentedButton = Ext.create("Ext.button.Segmented", {
      items: [me.sideFrontButton, me.sideRearButton],
    });

    me.facadeViewPanel = Ext.create("Ext.container.Container", {
      layout: "fit",
    });

    Ext.apply(me, {
      items: [me.facadeViewPanel],
      dockedItems: [
        {
          xtype: "toolbar",
          dock: "top",
          items: [me.reloadButton, "-", me.segmentedButton, me.zoomButton, me.downloadButton],
        },
      ],
    });
    me.callParent();
  },
  //
  preview: function(data){
    var me = this,
      side = me.segmentedButton.getValue(),
      schemeSVG = data.views[side === "front" ? 0 : 1].src;
    me.data = data;
    me.currentId = data.id;
    me.facadeViewPanel.removeAll();
    me.facadeViewPanel.add({
      xtype: "container",
      layout: "fit",
      items: [
        {
          xtype: "container",
          itemId: "scheme",
          filenamePrefix: `facade-${side}`,
          html: "<object id='svg-object' data='" + schemeSVG + "' type='image/svg+xml'></object>",
          listeners: {
            scope: me,
            afterrender: function(container){
              var app = this,
                svgObject = container.getEl().dom.querySelector("#svg-object");
              app.zoomButton.restoreZoom(); 
              me.addInteractionEvents(app, svgObject, app.app.showObject.bind(app.app));
            },
          },
        },
      ],
    });
    // me.startWidth = 0;
    // me.startHeight = 0;
    // if(me.isVisible()){
    //   me.startWidth = me.facadeViewPanel.getWidth();
    //   me.startHeight = me.facadeViewPanel.getHeight();
    // }
    me.sideRearButton.setDisabled(data.views.length < 2);
  },
  //
  onReload: function(){
    var me = this;
    me.mask("Loading...");
    Ext.Ajax.request({
      url: "/inv/inv/" + me.currentId + "/plugin/facade/",
      method: "GET",
      scope: me,
      success: function(response){
        me.preview(Ext.decode(response.responseText));
        me.unmask();
      },
      failure: function(){
        NOC.error(__("Failed to get data"));
        me.unmask();
      },
    });
  },
});
