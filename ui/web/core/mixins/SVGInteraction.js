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
              element.addEventListener(event, function(){
                var value = resourceData.split(":")[1];
                showObject(value);
              });
            }
            if(action === "info"){
              element.addEventListener(event, function(event){
                var scale = container.down("#zoomCombo").getValue();
                Ext.Ajax.request({
                  url: "/inv/inv/baloon/",
                  method: "POST",
                  jsonData: {
                    resource: resourceData,
                  },
                  success: function(response){
                    var result = Ext.decode(response.responseText),
                      path = Ext.Array.map(result.path, function(item){return item.label}).join(" > "),
                      tooltipHtml = `
                      <div>${path}</div>
                      <div><strong>${result.title}</strong></div>
                      <div><em>${result.description}</em></div>
                    `,
                      svgRect = svgObject.getBoundingClientRect(),
                      containerEl = container.getEl().dom,
                      xOffset = svgRect.left + containerEl.scrollLeft,
                      yOffset = svgRect.top + containerEl.scrollTop;

                    if(result.buttons){
                      tooltipHtml += `<div>${result.buttons}</div>`;
                    }
                    var tooltip = Ext.create("Ext.tip.ToolTip", {
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
                    });
                    tooltip.showAt([event.pageX * scale + xOffset, event.pageY * scale + yOffset]);
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