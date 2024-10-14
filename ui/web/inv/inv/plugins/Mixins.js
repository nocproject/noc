//---------------------------------------------------------------------
// inv.inv.plugins.mixins 
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.Mixins");

Ext.define("NOC.inv.inv.plugins.Mixins", {
  onDownloadSVG: function(){
    var _getFilenamePrefix = function(container){
        if(container.filenamePrefix){
          return container.filenamePrefix;
        }
        var panel = container.up("vizscheme");
        if(panel.itemId){
          return panel.itemId.replace("Panel", "").toLowerCase();
        }
        return "scheme";
      },
      me = this,
      currentId = me.getViewModel().get("currentId"),
      imageContainer = me.down("#schemeContainer"),
      filenamePrefix = _getFilenamePrefix(imageContainer),
      imageDom = imageContainer.getEl(),
      image = imageDom.dom.querySelector("svg") || imageDom.dom.querySelector("object").contentDocument,
      svgData = new XMLSerializer().serializeToString(image),
      blob = new Blob([svgData], {type: "image/svg+xml"}),
      url = URL.createObjectURL(blob),
      a = document.createElement("a");

    a.href = url;
    a.download = `${filenamePrefix}-${currentId}.svg`;
    a.click();
    URL.revokeObjectURL(url);
  },
});
