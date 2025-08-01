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
      currentId = this.getViewModel().get("currentId"),
      imageContainer = this.down("#schemeContainer"),
      filenamePrefix = _getFilenamePrefix(imageContainer),
      imageDom = imageContainer.getEl(),
      image = imageDom.dom.querySelector("svg") || imageDom.dom.querySelector("object").contentDocument,
      svgData = new XMLSerializer().serializeToString(image),
      blob = new Blob([svgData], {type: "image/svg+xml"});

    NOC.saveAs(blob, `${filenamePrefix}-${currentId}.svg`);

  },
  exportCSV: function(){
    var date = "_" + Ext.Date.format(new Date(), "YmdHis"),
      prefix = this.itemId.replace("Panel", "").toLowerCase(),
      filename = prefix + date + ".csv",
      grid = this.down("grid"),
      store = grid.getStore("gridStore"),
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
  setObservable: function(view){
    var observer = view.observer;
    if(Ext.isEmpty(observer)){
      observer = new IntersectionObserver(function(entries){
        view.isIntersecting = entries[0].isIntersecting;
      }, {
        threshold: 0.1,
      });
    }
    observer.observe(view.getEl().dom);
    return observer;
  },
  checkVisibility: function(isIntersecting){
    var isVisible = !document.hidden,
      isFocused = document.hasFocus();
    return isIntersecting && isVisible && isFocused;
  },
  reloadTask: function(callback, vm){
    var controller = this.getController();
    if(controller.checkVisibility(this.isIntersecting)){
      Ext.Function.bind(callback, controller)();
    } else{
      vm.set("icon", controller.generateIcon(true, "stop-circle-o", "grey", __("suspend")));
    }
  },
  generateIcon(isUpdatable, icon, color, msg){
    if(isUpdatable){
      return `<i class='fa fa-${icon}' style='padding-left:4px;color:${color};width:16px;' data-qtip='${msg}'></i>`;
    }
    return "<i class='fa fa-fw' style='padding-left:4px;width:16px;'></i>";
  },
});
