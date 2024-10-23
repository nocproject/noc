//---------------------------------------------------------------------
// inv.inv.plugins.mixins 
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.Mixins");

Ext.define("NOC.inv.inv.plugins.Mixins", {
  downloadSVG: function(){
    var _getFilenamePrefix = function(container){
        if(container.filenamePrefix){
          return container.filenamePrefix;
        }
        var panel = container.up("vizscheme, filescheme");
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
  showBalloon: function(app, itemId, resourceData, pos){
    Ext.Ajax.request({
      url: "/inv/inv/baloon/",
      method: "POST",
      jsonData: {
        resource: resourceData,
      },
      success: function(response){
        var result = Ext.decode(response.responseText),
          tooltipConfig = {},
          path = Ext.Array.map(result.path || [], function(item){
            if(!item.id){
              return `<span>${item.label}</span>`
            }
            return `<span style='cursor: pointer;text-decoration: underline;'`
                    + `data-item-id="${item.id}"`
                    + `>${item.label}</span>`
          }).join(" > "),
          tooltipHtml = `
                      ${path}
                      <div style='padding: 4px 0;'><em>${result.description}</em></div>
                    `

        Ext.ComponentQuery.query("tooltip#" + itemId).forEach(function(tooltip){
          tooltip.destroy();
        });
                      
        tooltipConfig = {
          itemId: itemId,
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
                  app.showObject(value);
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
                    app.showObject(button.args);
                  }
                },
              }
            }),
          });
        }

        var tooltip = Ext.create("Ext.tip.ToolTip", tooltipConfig);
        tooltip.showAt(pos);
      },
      failure: function(){
        NOC.error(__("Failed to get data"));
      },
    });
  },
  exportCSV: function(){
    var date = "_" + Ext.Date.format(new Date(), "YmdHis"),
      prefix = this.itemId.replace("Panel", "").toLowerCase(),
      filename = prefix + date + ".csv",
      grid = this.down("grid"),
      store = this.getViewModel().getStore("gridStore"),
      records = store.getData().items,
      columns = grid.getColumns().map(function(column){
        return {
          dataIndex: column.dataIndex,
        };
      });
    this.downloadCsv(
      new Blob([this.export(records, columns)],
               {type: "text/plain;charset=utf-8"}),
      filename,
    );
  },
});
