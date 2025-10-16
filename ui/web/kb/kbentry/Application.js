//---------------------------------------------------------------------
// kb.kbentry application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.kb.kbentry.Application");

Ext.define("NOC.kb.kbentry.Application", {
  extend: "NOC.core.ModelApplication",
  layout: "card",
  requires: [
    "NOC.core.ListFormField",
    "NOC.core.label.LabelField",
    "NOC.kb.kbentry.Model",
    "NOC.kb.kbentry.HistoryPanel",
    "NOC.main.language.LookupField",
    "NOC.main.ref.kbparser.LookupField",
    "Ext.ux.grid.column.GlyphAction",
  ],
  model: "NOC.kb.kbentry.Model",
  itemId: "kbentryApp",
  search: true,
  initComponent: function(){
    var me = this;

    me.historyButton = Ext.create("Ext.button.Button", {
      text: __("History"),
      glyph: NOC.glyph.history,
      scope: me,
      handler: me.onHistory,
    });

    me.ITEM_HISTORY = me.registerItem("NOC.kb.kbentry.HistoryPanel");

    me.listForm = Ext.create({
      xtype: "listform",
      name: "attachments",
      rows: 5,
      fieldLabel: __("Attachments"),
      onDeleteRecord: me.deleteFromList,
      items:
                [
                  {
                    layout: "hbox",
                    border: false,
                    items: [
                      {
                        xtype: "displayfield",
                        name: "name",
                        fieldLabel: __("File name"),
                        allowBlank: true,
                        flex: 3,
                      },
                      {
                        xtype: "filefield",
                        name: "file",
                        flex: 1,
                        buttonOnly: true,
                        hideLabel: true,
                        buttonText: __("Select File..."),
                        listeners: {
                          change: me.setAttachmentName,
                        },
                      },
                    ],
                  },
                  {
                    xtype: "textfield",
                    name: "description",
                    fieldLabel: __("Description"),
                    width: "75%",
                  },
                  {
                    xtype: "checkboxfield",
                    name: "is_hidden",
                    fieldLabel: __("Is Hidden"),
                    width: "75%",
                    allowBlank: true,
                  },
                ],
    });

    Ext.apply(me, {
      columns: [
        {
          xtype: "glyphactioncolumn",
          width: 20,
          sortable: false,
          items: [
            {
              glyph: NOC.glyph.eye,
              tooltip: __("Show KB"),
              handler: me.onShowKB,
            },
          ],
        },
        {
          text: __("Subject"),
          dataIndex: "subject",
        },
        {
          text: __("Language"),
          dataIndex: "language",
          renderer: NOC.render.Lookup("language"),
        },
        {
          text: __("Labels"),
          dataIndex: "labels",
          renderer: NOC.render.LabelField,
        },
      ],
      fields: [
        {
          name: "subject",
          xtype: "textfield",
          fieldLabel: __("Subject"),
          allowBlank: false,
        },
        {
          name: "body",
          xtype: "htmleditor",
          fieldLabel: __("Body"),
          allowBlank: false,
        },
        {
          name: "language",
          xtype: "main.language.LookupField",
          fieldLabel: __("Language"),
          allowBlank: false,
          query: {
            "is_active": true,
          },
        },
        {
          name: "markup_language",
          xtype: "main.ref.kbparser.LookupField",
          fieldLabel: __("Markup Language"),
          allowBlank: false,
        },
        {
          name: "labels",
          xtype: "labelfield",
          fieldLabel: __("Labels"),
          allowBlank: true,
          query: {
            "enable_kbentry": true,
          },
        },
        me.listForm,
      ],
      formToolbar: [
        me.historyButton,
      ],
    });
    me.callParent();
  },
  onShowKB: function(view, rowIndex, colIndex, item, e, record){
    window.open(
      "/api/card/view/kb/" + record.id + "/",
    );
  },
  onHistory: function(){
    var me = this;
    me.previewItem(me.ITEM_HISTORY, me.currentRecord);
  },
  onSave: function(){
    var me = this,
      data = new FormData();
    data.append("subject", me.down("[name=subject]").getValue());
    data.append("body", me.down("[name=body]").getValue());
    data.append("language", me.down("[name=language]").getValue());
    data.append("markup_language", me.down("[name=markup_language]").getValue());
    data.append("labels", me.down("[name=labels]").getValue());
    Ext.each(me.query("[name=attachments] > form > form"), function(form, indx){
      var file = form.down("[name=file]");
      if(file.getValue()){
        data.append("file" + indx, file.fileInputEl.dom.files[0]);
        data.append("description" + indx, form.down("[name=description]").getValue());
        data.append("is_hidden" + indx, form.down("[name=is_hidden]").getValue());
      }
    });
    Ext.Ajax.request({
      method: "POST",
      url: me.base_url + (me.currentRecord ? me.currentRecord.get([me.idField]) + "/" : ""),
      rawData: data,
      headers: {"Content-Type": null},
      scope: me,
      success: function(){
        var me = this;
        me.showItem(me.ITEM_GRID);
        me.reloadStore();
        NOC.info(__("Records has been saved"));
      },
      failure: function(){
        NOC.error(__("Failed"));
      },
    });
  },
  setAttachmentName: function(field, value){
    var filename = value.replace(/(^.*([\\/]))?/, "");
    field.previousSibling().setValue(filename)
  },
  deleteFromList: function(){
    var me = this,
      app = me.up("[itemId=kbentryApp]"),
      filename = me.panel.getComponent(me.currentSelection).down("[name=name]").getValue();
    Ext.Ajax.request({
      method: "DELETE",
      url: app.base_url + app.currentRecord.id + "/attachment/" + filename + "/",
      success: function(){
        me.deleteRecord();
        NOC.info(__("Attachment deleted"));
      },
      failure: function(){
        NOC.error(__("Failed"));
      },
    });
  },
});
