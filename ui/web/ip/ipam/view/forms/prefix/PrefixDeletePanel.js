//---------------------------------------------------------------------
// ip.ipam Delete Prefix Panel
//---------------------------------------------------------------------
// Copyright (C) 2007-2019 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.ip.ipam.view.forms.prefix.PrefixDeletePanel");

Ext.define("NOC.ip.ipam.view.forms.prefix.PrefixDeletePanel", {
  extend: "Ext.form.Panel",
  layout: "vbox",
  alias: "widget.ip.ipam.form.delete.prefix",
  style: "border: none",
  app: undefined,
  viewModel: {
    data: {
      deleteType: "none",
      prefix: "-",
      description: "-",
    },
    formulas: {
      canDelete: {
        bind: {
          bindTo: "{deleteType}",
        },
        get: function(t){
          return t && t !== "none" && t.delete_type !== "none"
        },
      },
    },
  },
  currentPrefixId: null,
  parentPrefixId: null,

  initComponent: function(){
    var me = this;
    Ext.apply(me, {
      items: [
        {
          bind: {
            html: "<h1>Delete prefix {prefix}?</h1>" +
                        "You're trying to delete prefix {prefix} ({description})<br>" +
                        "<b>Warning!</b> This action cannot be undone!</b>",
          },
        },
        {
          xtype: "radiogroup",
          columns: 1,
          vertical: true,
          simpleValue: true,
          bind: "{deleteType}",
          items: [
            {
              boxLabel: __("Do not delete"),
              name: "delete_type",
              inputValue: "none",
              checked: true,
            },
            {
              boxLabel: __("Delete prefix and save and relink the nested prefixes and addresses?"),
              name: "delete_type",
              inputValue: "p",
            },
            {
              boxLabel: __("Delete prefix and all nested prefixes, addresses and permissions?"),
              name: "delete_type",
              inputValue: "r",
            },
          ],
        },
      ],
      dockedItems: [{
        dock: "top",
        xtype: "toolbar",
        items: [
          {
            text: __("Close"),
            tooltip: __("Close without deleting"),
            glyph: NOC.glyph.arrow_left,
            scope: me,
            handler: me.onClose,
          },
          "-",
          {
            text: __("Delete"),
            tooltip: __("Delete Prefix"),
            glyph: NOC.glyph.trash,
            scope: me,
            handler: me.onDelete,
            bind: {
              disabled: "{!canDelete}",
            },
          },
        ],
      }],
    });
    me.callParent();
  },

  preview: function(id){
    var me = this;
    Ext.Ajax.request({
      url: "/ip/prefix/" + id + "/",
      method: "GET",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText);
        me.currentPrefixId = id;
        me.parentPrefixId = data.parent;
        me.viewModel.set("prefix", data.prefix);
        me.viewModel.set("description", data.description);
      },
      failure: function(){
        NOC.error(__("Failed to load data"))
      },
    })
  },

  onClose: function(){
    var me = this;
    me.fireEvent("ipIPAMPrefixDeleteFormClose", {id: me.currentPrefixId});
  },

  onDelete: function(){
    var me = this,
      isRecursive = me.viewModel.get("deleteType").delete_type === "r",
      url = "/ip/prefix/" + me.currentPrefixId + "/";
    if(isRecursive){
      url += "recursive/"
    }
    Ext.Ajax.request({
      url: url,
      method: "DELETE",
      scope: me,
      success: function(){
        NOC.info(__("Prefix Deleted"));
        me.fireEvent("ipIPAMParentPrefixOpen");
      },
      failure: function(){
        NOC.error(__("Failed to load data"))
      },
    })
  },
});