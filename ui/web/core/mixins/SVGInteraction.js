//---------------------------------------------------------------------
// NOC.core.mixins.SVGInteraction
// Add Interactive to SVG
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.mixins.SVGInteraction");

Ext.define("NOC.core.mixins.SVGInteraction", {
  addInteractionEvents: function(svgObject, showObject){
    svgObject.addEventListener('load', function(){
      var svgDocument = svgObject.contentDocument;
      if(svgDocument){
        var svgElements = svgDocument.querySelectorAll("[data-interaction]");
        svgElements.forEach(function(element){
          var events = element.dataset.interaction.split(",");
          events.forEach(function(e){
            var [event, action, resource] = e.split(":");
            if(action === "go"){
              element.addEventListener(event, function(){
                var value = decodeURIComponent(resource).split(":")[1];
                showObject(value);
              });
            }
          });
        });
      } else{
        NOC.error(__("SVG Document is not loaded"));
      }
    });
  },
});