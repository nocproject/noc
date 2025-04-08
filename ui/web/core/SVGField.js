//---------------------------------------------------------------------
// NOC.core.SVGField
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.SVGField");

Ext.define("NOC.core.SVGField", {
  extend: "Ext.form.field.Base",
  alias: "widget.svgfield",

  config: {
    accept: ".svg",
    uploadIcon: NOC.glyph.upload,
    downloadIcon: NOC.glyph.download,
  },

  fieldSubTpl: [
    "<div style='display: flex'>",
    '<img id="{cmpId}-inputEl-imageEl" src="" height="100" width="100" class="x-hidden">',
    "<div style='display: flex; flex-direction: column;padding-left: 10px;gap: 10px;'>",
    '<input id="{cmpId}-inputEl-fileInputEl" type="file" accept="{accept}" style="display:none">',
    '<label for="{cmpId}-inputEl-fileInputEl" class="x-btn x-btn-default-toolbar-small" style="height:32px">',
    '<span style="font-family:FontAwesome" class="x-btn-glyph x-btn-icon-el-default-toolbar-small">{uploadIcon}</span>',
    '<span class="x-btn-innner x-btn-inner-default-toolbar-small">',
    __("Select Image..."),
    "</span>",
    "</label>",
    '<input id="{cmpId}-inputEl-fileDownloadEl" type="button" style="display:none">',
    '<label for="{cmpId}-inputEl-fileDownloadEl" class="x-btn x-btn-default-toolbar-small x-item-disabled x-btn-disabled" style="height:32px">',
    '<span style="font-family:FontAwesome" class="x-btn-glyph x-btn-icon-el-default-toolbar-small">{downloadIcon}</span>',
    '<span class="x-btn-innner x-btn-inner-default-toolbar-small">',
    __("Download Image..."),
    "</span>",
    "</label>",
    "</div>",
    "</div>",
  ],

  initComponent: function(){
    var me = this;
    me.callParent();
    me.on("afterrender", me.setupElements, me);
  },

  getSubTplData: function(data){
    var me = this,
      args;
    args = me.callParent([data]);
    args.accept = me.accept || null;
    args.uploadIcon = "&#x" + me.uploadIcon.toString(16) + ";";
    args.downloadIcon = "&#x" + me.downloadIcon.toString(16) + ";";
    return args;
  },

  setupElements: function(){
    var me = this,
      idPrefix = "#" + me.getInputId();
    me.fileEl = me.el.down(idPrefix + "-fileInputEl");
    me.fileEl.on("change", me.onFileChange, me);
    me.downloadEl = me.el.down(idPrefix + "-fileDownloadEl");
    me.downloadEl.on("click", me.onDownloadFile, me);
    me.imageEl = me.el.down(idPrefix + "-imageEl");
  },

  onDownloadFile: function(){
    var data = this.getValue();
    if(Ext.isEmpty(data)){
      return;
    }
    this.fireEvent("download", this, data);
  },

  downloadFile: function(filename, data){
    NOC.saveAs(new Blob([data], {type: "image/svg+xml;charset=utf-8"}), filename);
  },

  onFileChange: function(){
    var reader,
      me = this,
      file = me.fileEl.dom.files[0];
    if(!file){
      return;
    }
    reader = new FileReader();
    reader.onload = function(event){
      var contents = event.target.result;
      me.setValue(contents); // Directly set the data
      // Trigger change event
      me.fireEvent("change", me, contents);
    };
    reader.onerror = function(){
      NOC.error(__("Cannot read file"));
    };
    reader.readAsText(file);
  },

  setValue: function(data){
    var me = this,
      classes = ["x-item-disabled", "x-btn-disabled"],
      downloadLabel = me.el.down("label[for=" + me.getInputId() + "-fileDownloadEl]");
    if(data === ""){
      me.imageEl.addCls("x-hidden");
      downloadLabel.dom.classList.add(...classes);
    } else{
      // Update the src attribute of the existing img tag to display the new SVG content
      me.imageEl.set({
        src: "data:image/svg+xml," + encodeURIComponent(data),
      });
      // Make visible
      me.imageEl.removeCls("x-hidden");
      downloadLabel.dom.classList.remove(...classes);
    }
    // Call parent's setData method
    me.callParent(arguments);
  },
});
