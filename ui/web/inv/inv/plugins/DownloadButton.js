//---------------------------------------------------------------------
// inv.inv.plugins.DownloadButton widget
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.DownloadButton");

Ext.define("NOC.inv.inv.plugins.DownloadButton", {
  extend: "Ext.button.Split",
  mixins: [
    "NOC.inv.inv.plugins.Mixins",
  ],
  alias: "widget.invPluginsDownloadButton",
  glyph: NOC.glyph.download,
  defaultListenerScope: true,
  selectedMenuItem: "SVG", // Default selected item
  viewModel: {
    formulas: {
      buttonDisabled: function(get){
        return get("downloadCsvButtonDisabled") && get("downloadSvgButtonDisabled");
      },
    },
  },
  bind: {
    disabled: "{buttonDisabled}",
  },
  menu: [
    {
      xtype: "menucheckitem",
      text: "CSV",
      handler: "onMenuSelect",
      itemId: "csvMenuItem",
      bind: {
        disabled: "{downloadCsvButtonDisabled}",
      },
    },
    {
      xtype: "menucheckitem",
      text: "SVG",
      handler: "onMenuSelect",
      itemId: "svgMenuItem",
      bind: {
        disabled: "{downloadSvgButtonDisabled}",
      },
    },
  ],
  listeners: {
    afterrender: "updateMenuCheckMarks",
    click: "onButtonClick",
  },
  onMenuSelect: function(item){
    this.selectedMenuItem = item.itemId === "csvMenuItem" ? "CSV" : "SVG";
    this.updateMenuCheckMarks();
    item.up("menu").hide();
  },
  updateMenuCheckMarks: function(){
    this.menu.items.each(function(item){
      item.setChecked(item.itemId === (this.selectedMenuItem === "CSV" ? "csvMenuItem" : "svgMenuItem"));
      this.setText(this.selectedMenuItem);
      this.setTooltip(__("Download") + " " + this.selectedMenuItem);
    }, this);
  },
  onButtonClick: function(){
    NOC.info(__("Download button clicked") + " " + this.selectedMenuItem);
    if(this.selectedMenuItem === "CSV"){
      this.onExportCSV();
    } else{
      Ext.bind(this.onDownloadSVG, this.up("vizscheme"))();
    }
  },
  onExportCSV: function(){
    console.log("Export CSV");
  },
});