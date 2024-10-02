//---------------------------------------------------------------------
// NOC.core.mixins.SVGInteraction
// Add Interactive to SVG
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.mixins.SVGInteraction");

Ext.define("NOC.core.mixins.SVGInteraction", {
  addInteractionEvents: function(container, svgObject, showObject){
    svgObject.addEventListener("load", function(){
      var svgDocument = svgObject.contentDocument;
      
      if(svgDocument){
        var elements = svgDocument.querySelectorAll("[data-interaction]");
        elements.forEach(function(element){
          var events = element.dataset.interaction.split(",");
          events.forEach(function(e){
            var [event, action, resource] = e.split(":"),
              resourceData = decodeURIComponent(resource);
            if(action === "go"){
              element.addEventListener(event, function(evt){
                var value = resourceData.split(":")[1];
                evt.stopPropagation();
                showObject(value);
              });
            }
            if(action === "info"){
              element.addEventListener(event, function(evt){
                var scale = container.down("#zoomCombo").getValue();
                evt.stopPropagation();
                Ext.Ajax.request({
                  url: "/inv/inv/baloon/",
                  method: "POST",
                  jsonData: {
                    resource: resourceData,
                  },
                  success: function(response){
                    var result = Ext.decode(response.responseText),
                      tooltipConfig = {},
                      path = Ext.Array.map(result.path, function(item){
                        return `<span style='cursor: pointer;text-decoration: underline;'`
                        + `data-item-id="${item.id}"`
                          + `>${item.label}</span>`
                      }).join(" > "),
                      tooltipHtml = `
                      ${path}
                      <div style='padding: 4px 0;'><em>${result.description}</em></div>
                    `,
                      svgRect = svgObject.getBoundingClientRect(),
                      containerEl = container.getEl().dom,
                      xOffset = svgRect.left + containerEl.scrollLeft,
                      yOffset = svgRect.top + containerEl.scrollTop;

                    Ext.ComponentQuery.query("tooltip#SVGbaloon").forEach(function(tooltip){
                      tooltip.destroy();
                    });
                      
                    tooltipConfig = {
                      itemId: "SVGbaloon",
                      title: result.title,
                      padding: "4 0",
                      html: tooltipHtml,
                      closeAction: "destroy",
                      dismissDelay: 0,
                      tools: [
                        {
                          type: "close",
                          handler: function(){
                            tooltip.destroy();
                          },
                        },
                      ],
                      listeners: {
                        afterrender: function(tooltip){
                          var items = tooltip.el.query("[data-item-id]");
                          items.forEach(function(element){
                            element.addEventListener("click", function(evt){
                              var value = element.dataset.itemId;
                              evt.stopPropagation(); 
                              showObject(value);
                            }); 
                          });
                        },
                      },
                    }
                    if(result.buttons && result.buttons.length){
                      Ext.apply(tooltipConfig, {
                        buttons: Ext.Array.map(result.buttons, function(button){ 
                          return {
                            xtype: "button",
                            glyph: button.glyph,
                            tooltip: button.hint,
                            handler: function(){
                              if(button.action === "go"){
                                showObject(button.args);
                              }
                            },
                          }
                        }),
                      });
                    }

                    var tooltip = Ext.create("Ext.tip.ToolTip", tooltipConfig);
                    tooltip.showAt([evt.pageX * scale + xOffset, evt.pageY * scale + yOffset]);
                  },
                  failure: function(){
                    NOC.error(__("Failed to get data"));
                  },
                });
              })
            }
          });
        });
      } else{
        NOC.error(__("SVG Document is not loaded"));
      }
    });
  },
});