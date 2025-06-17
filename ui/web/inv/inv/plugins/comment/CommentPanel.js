//---------------------------------------------------------------------
// inv.inv Comment panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.inv.plugins.comment.CommentPanel");

Ext.define("NOC.inv.inv.plugins.comment.CommentPanel", {
  extend: "Ext.panel.Panel",
  requires: [
    "NOC.core.MarkdownEditor",
  ],
  title: __("Comment"),
  closable: false,
  layout: "fit",
  scrollable: true,
  padding: 4,

  initComponent: function(){
    var me = this;

    me.displayField = Ext.create("Ext.container.Container", {
      autoScroll: true,
    });

    // me.editField = Ext.create("Ext.form.field.HtmlEditor", {
    //   hidden: true,
    //   defaultLinkValue: "https://",
    //   createLink: function(){
    //     var url = prompt(this.createLinkText, this.defaultLinkValue);
    //     if(url && url !== this.defaultLinkValue){
    //       this.relayCmd("insertHTML", "<a href='" + url + "' target='_blank'>" + url + "</a>");
    //     }
    //   },
    // });

    me.editField = Ext.create("NOC.core.MarkdownEditor", {
      hidden: true,
    });

    me.editButton = Ext.create("Ext.button.Button", {
      text: __("Edit"),
      glyph: NOC.glyph.edit,
      scope: me,
      handler: me.onEdit,
    });

    me.saveButton = Ext.create("Ext.button.Button", {
      text: __("Save"),
      glyph: NOC.glyph.save,
      scope: me,
      handler: me.onSave,
      hidden: true,
    });

    // Grids
    Ext.apply(me, {
      items: [
        me.displayField,
        me.editField,
      ],
      dockedItems: [{
        xtype: "toolbar",
        dock: "top",
        padding: "0 0 4 0",
        items: [
          me.editButton,
          me.saveButton,
        ],
      }],
    });
    me.callParent();
  },
  //
  preview: function(data){
    var me = this;
    me.currentId = data.id;
    me.displayField.update(data.comment);
    me.editField.setValue(data.comment);
  },
  //
  onEdit: function(){
    var me = this;
    me.editButton.hide();
    me.saveButton.show();
    me.displayField.hide();
    me.editField.show();
  },
  //
  onSave: function(){
    var me = this,
      value = me.editField.getValue();
    Ext.Ajax.request({
      url: "/inv/inv/" + me.currentId + "/plugin/comment/",
      method: "POST",
      jsonData: {
        comment: value,
      },
      scope: me,
      success: function(){
        me.editButton.show();
        me.saveButton.hide();
        me.editField.hide();
        me.displayField.update(value);
        me.displayField.show();
      },
      failure: function(){
        NOC.error(__("Failed to save data"));
      },
    });
  },
});
