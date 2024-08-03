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
            // {
            // xtype: "image",
            // itemId: "image",
            // src: view.src,
            // title: view.name,
            // padding: 5,
            // },
            {
              xtype: "container",
              itemId: "image",
              html: "<object id='svg-object' data=" + view.src + "' type='image/svg+xml'></object>",
              padding: 5,
              listeners: {
                scope: me,
                afterrender: function(container){
                  var app = this,
                    svgObject = container.getEl().dom.querySelector('#svg-object');
                  svgObject.addEventListener('load', function(){
                    var svgDocument = svgObject.contentDocument;
                    if(svgDocument){
                      var selectableElements = svgDocument.querySelectorAll('.selectable rect');
                      if(selectableElements.length > 0){
                        selectableElements.forEach(function(element){
                          element.addEventListener('mouseover', function(){
                            element.style.fill = 'blue';
                          });
                          element.addEventListener('mouseout', function(){
                            element.style.fill = 'rgb(30, 112, 186)';
                          });
                        });
                      } else{
                        console.error("Selectable element not found");
                      }

                      var svgElements = svgDocument.querySelectorAll("[data-event]");
                      svgElements.forEach(function(element){
                        var events = element.dataset.event.split(",");
                        events.forEach(function(event){
                          element.addEventListener(event, function(){
                            app.app.showObject(element.dataset.resource.split(":")[1]);
                          });
                        });
                      });
                    } else{
                      NOC.error(__("SVG Document is not loaded"));
                    }
                  });
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
    me.zoomButton.setValue(1.0);
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
    var me = this,
      width = me.startWidth,
      height = me.startHeight;
    Ext.each(me.query("#image"), function(img){
      var imgEl = img.getEl().dom;
      imgEl.style.transformOrigin = "0 0";
      imgEl.style.transform = "scale(" + combo.getValue() + ")";
      width = Math.max(width, imgEl.width);
      height = Math.max(height, imgEl.height);
      me.facadeViewPanel.setWidth(width);
    });
  },
});
