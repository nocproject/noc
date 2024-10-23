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
  selectedMenuItem: "svgMenuItem", // Default selected item
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
    this.selectedMenuItem = item.itemId;
    this.updateMenuCheckMarks();
    item.up("menu").hide();
  },
  updateMenuCheckMarks: function(){
    this.menu.items.each(function(item){
      var buttonText = this.selectedMenuItem === "csvMenuItem" ? "CSV" : "SVG";
      item.setChecked(item.itemId === this.selectedMenuItem);
      this.setText(buttonText);
      this.setTooltip(__("Download") + " " + buttonText);
    }, this);
  },
  onButtonClick: function(){
    NOC.info(__("Download button clicked") + " " + this.selectedMenuItem);
    if(this.selectedMenuItem === "csvMenuItem"){
      Ext.bind(this.exportCSV, this.up("vizscheme"))();
    } else if(this.selectedMenuItem === "svgMenuItem"){
      Ext.bind(this.downloadSVG, this.up("vizscheme"))();
    }
  },
});