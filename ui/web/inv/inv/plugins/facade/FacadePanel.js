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
        me.viewCard.setActiveItem(0);
      },
    });

    me.sideRearButton = Ext.create("Ext.button.Button", {
      glyph: NOC.glyph.hand_o_left,
      text: __("Rear"),
      scope: me,
      toggleGroup: "side",
      value: "rear",
      handler: function(){
        me.viewCard.setActiveItem(1);
      },
    });

    me.zoomButton = Ext.create("NOC.inv.inv.plugins.Zoom", {
      itemId: "zoomControl",
      appPanel: me.itemId,
      setZoom: me.setZoom,
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

    me.viewCard = Ext.create("Ext.container.Container", {
      xtype: "container",
      layout: "card",
      activeItem: 0,
    });

    me.facadeViewPanel = Ext.create("Ext.container.Container", {
      layout: "fit",
      items: [me.viewCard],
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
    var me = this;
    me.currentId = data.id;
    // Remove all views
    if(me.viewCard.items.length > 0) me.viewCard.removeAll();
    // Add views
    me.viewCard.add(
      Ext.Array.map(data.views, function(view, index){
        return {
          xtype: "container",
          layout: "fit",
          items: [
            {
              xtype: "container",
              itemId: "image-" + (index === 0 ? "front" : "rear"),
              html: "<object id='svg-object' data='" + view.src + "' type='image/svg+xml'></object>",
              padding: 5,
              listeners: {
                scope: me,
                afterrender: function(container){
                  var app = this,
                    svgObject = container.getEl().dom.querySelector("#svg-object");
                  app.zoomButton.setZoom(app.zoomButton); 
                  me.addInteractionEvents(app, svgObject, app.app.showObject.bind(app.app));
                },
              },
            },
          ],
        };
      }),
    );
    me.startWidth = 0;
    me.startHeight = 0;
    if(me.isVisible()){
      me.startWidth = me.facadeViewPanel.getWidth();
      me.startHeight = me.facadeViewPanel.getHeight();
    }
    // Reset zoom
    // me.zoomButton.setValue(1.0);
    // Disable rear button if necessary
    me.sideRearButton.setDisabled(data.views.length < 2);
    // Press front button
    me.sideFrontButton.setPressed(true);
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
  //
  setZoom: function(combo){
    var me = this.up("#facadePanel"),
      width = me.startWidth,
      height = me.startHeight;
    Ext.each(me.query("#image-front, #image-rear"), function(img){
      var imgEl = img.getEl().dom;
      imgEl.style.transformOrigin = "0 0";
      imgEl.style.transform = "scale(" + combo.getValue() + ")";
      width = Math.max(width, imgEl.width);
      height = Math.max(height, imgEl.height);
      me.facadeViewPanel.setWidth(width);
    });
  },
  //
  onDownloadSVG: function(){
    var me = this,
      side = me.segmentedButton.getValue(),
      svg = me.viewCard.down(`#image-${side}`).getEl().dom.querySelector("object").contentDocument.documentElement.outerHTML,
      blob = new Blob([svg], {type: "image/svg+xml"}),
      url = URL.createObjectURL(blob),
      a = document.createElement("a");
    a.href = url;
    a.download = `facade-${side}-${me.currentId}.svg`;
    a.click();
    URL.revokeObjectURL(url);
  },
});
