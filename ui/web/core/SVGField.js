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

  requires: ["Ext.form.field.File"],
  config: {
    accept: ".svg",
  },

  fieldSubTpl: [
    "<div style='display:flex;'>",
    '<img id="{cmpId}-inputEl-imageEl" src="" height="100" width="100">',
    '<input id="{cmpId}-inputEl-fileInputEl" type="file" accept="{accept}">',
    "</div>",
  ],

  initComponent: function () {
    var me = this;
    me.callParent();
    me.on("afterrender", me.setupElements, me);
  },

  getSubTplData: function (data) {
    var me = this,
      args;
    args = me.callParent([data]);
    args.accept = me.accept || null;
    console.log(">", args);
    return args;
  },

  setupElements: function () {
    var me = this;
    idPrefix = "#" + me.getInputId();
    me.fileEl = me.el.down(idPrefix + "-fileInputEl");
    me.fileEl.on("change", me.onFileChange, me);
    me.imageEl = me.el.down(idPrefix + "-imageEl");
  },

  onFileChange: function (fileField, value, eOpts) {
    var me = this;

    var file = me.fileEl.dom.files[0];

    if (!file) {
      return;
    }

    var reader = new FileReader();

    reader.onload = function (event) {
      var contents = event.target.result;
      me.setValue(contents); // Directly set the data
      // Trigger change event
      me.fireEvent("change", me, contents);
    };

    reader.onerror = function (event) {
      NOC.error(__("Cannot read file"));
    };

    reader.readAsText(file);
  },

  setValue: function (data) {
    var me = this;

    // Call parent's setData method
    me.callParent(arguments);

    // Update the src attribute of the existing img tag to display the new SVG content
    me.imageEl.set({
      src: "data:image/svg+xml," + encodeURIComponent(data),
    });
  },
});
