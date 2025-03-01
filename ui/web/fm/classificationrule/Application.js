//---------------------------------------------------------------------
// fm.classificationrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2013 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.fm.classificationrule.Application");

Ext.define("NOC.fm.classificationrule.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreview",
    "NOC.core.TemplatePreview",
    "NOC.core.StringListField",
    "NOC.core.tagfield.Tagfield",
    "NOC.core.ListFormField",
    "NOC.fm.classificationrule.Model",
    "NOC.fm.classificationrule.TestForm",
    "NOC.fm.eventclass.LookupField",
    "NOC.main.label.LookupField",
    "NOC.sa.profile.LookupField",
    "Ext.ux.form.JSONField",
    "Ext.ux.form.GridField",
    "Ext.form.field.Tag",
  ],
  model: "NOC.fm.classificationrule.Model",
  search: true,
  treeFilter: "category",
  columns: [
    {
      text: __("Name"),
      dataIndex: "name",
      width: 500,
    },
    {
      text: __("Builtin"),
      dataIndex: "is_builtin",
      width: 50,
      renderer: NOC.render.Bool,
    },
    {
      text: __("Event Class"),
      dataIndex: "event_class",
      flex: 1,
      renderer: NOC.render.Lookup("event_class"),
    },
    {
      text: __("Pref"),
      dataIndex: "preference",
      width: 50,
    },
  ],
  filters: [
    {
      title: __("By Event Class"),
      name: "event_class",
      ftype: "lookup",
      lookup: "fm.eventclass",
    },
  ],

  initComponent: function(){
    var me = this;
    me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
      app: me,
      restUrl: new Ext.XTemplate("/fm/classificationrule/{id}/json/"),
      previewName: new Ext.XTemplate("Classification Rule: {name}"),
    });
    me.ITEM_JSON = me.registerItem(me.jsonPanel);
    //
    me.testForm = Ext.create("NOC.fm.classificationrule.TestForm", {
      app: me,
    });
    me.ITEM_TEST_FORM = me.registerItem(me.testForm);
    //
    me.testResultPanel = Ext.create("NOC.core.TemplatePreview", {
      app: me,
      previewName: new Ext.XTemplate("Rule Test Result"),
      template: new Ext.XTemplate('<div class="noc-tp">\n    <tpl if="errors">\n        <i class="icon-warning-sign"></i><b>Errors:</b><br/>\n        <tpl foreach="errors">\n            {.}<br/>\n        </tpl>\n    </tpl>\n    <b>Result:</b>\n    <tpl if="result">\n        <i class="fa fa-check"></i> Matched\n        <tpl else><i class="fa fa-exclamation-triangle"></i> Not matched\n    </tpl>\n    <br/>\n    <br/>\n    <b>Fetched variables:</b><br/>\n    <table border="1">\n        <thead>\n        <th>Name</th>\n        <th>Value</th>\n        </thead>\n        <tbody>\n        <tpl foreach="vars">\n            <tr>\n                <td><b>{key}</b></td>\n                <td>{value}</td>\n            </tr>\n        </tpl>\n        </tbody>\n    </table>\n    <br/>\n    <b>Patterns:</b><br/>\n    <table border="1">\n        <tr>\n            <th rowspan="2"\n            </th>\n            <th colspan="2">Key</th>\n            <th colspan="2">Value</th>\n            <th rowspan="2">Vars</th>\n        </tr>\n        <tr>\n            <th>Key</th>\n            <th>Key Pattern</th>\n            <th>Value</th>\n            <th>Value Pattern</th>\n        </tr>\n        <tpl foreach="patterns">\n\n            <tr>\n                <td>\n                    <tpl if="status">\n                    <i class="fa fa-check"></i>\n                    <tpl else><i class="fa fa-exclamation-triangle"></i></tpl>\n                </td>\n                <td>{key}</td>\n                <td>{key_re}</td>\n                <td>{value}</td>\n                <td>{value_re}</td>\n                <td>\n                    <tpl if="vars">\n                        <tpl foreach="vars">\n                            <b>{key}:</b> {value}<br/>\n                        </tpl>\n                    </tpl>\n                </td>\n            </tr>\n        </tpl>\n    </table>\n    <br/>\n    <div style="border: 1px dotted #808080">\n        <b>Subject:</b> {subject}<br/>\n        {body}\n    </div>\n</div>'),
      onCloseItem: "ITEM_FORM",
    });
    me.ITEM_TEST_RESULT = me.registerItem(me.testResultPanel);
    //
    Ext.apply(me, {
      fields: [
        {
          xtype: "textfield",
          name: "name",
          fieldLabel: __("Name"),
          allowBlank: false,
        },
        {
          xtype: "displayfield",
          name: "uuid",
          fieldLabel: __("UUID"),
        },
        {
          xtype: "textarea",
          name: "description",
          fieldLabel: __("Description"),
          allowBlank: true,
        },
        {
          xtype: "fieldset",
          layout: "hbox",
          title: __("Match"),
          labelAlign: "right",
          defaults: {
            padding: 4,
            labelAlign: "right",
          },
          items: [
            {
              xtype: "numberfield",
              name: "preference",
              fieldLabel: __("Preference"),
              allowBlank: false,
              uiStyle: "small",
              defaultValue: 1000,
              minValue: 0,
              maxValue: 10000,
            },
            {
              name: "sources",
              xtype: "tagfield",
              fieldLabel: __("Sources"),
              allowBlank: false,
              store: [
                ["syslog", __("SYSLOG")],
                ["SNMP Trap", __("SNMP_TRAP")],
                ["other", __("OTHER")],
              ],
              uiStyle: "medium",
            },
            {
              xtype: "fm.eventclass.LookupField",
              name: "event_class",
              fieldLabel: __("Event Class"),
              allowBlank: false,
              uiStyle: "large",
              listeners: {
                select: {
                  scope: me,
                  fn: me.onSelectEventClass,
                },
              },
            },
          ],
        },
        {
          xtype: "core.tagfield",
          url: "/sa/profile/lookup/",
          fieldLabel: __("Profiles"),
          tooltip: __("SA Profiles, for match rules"),
          name: "profiles",
          uiStyle: "large",
          listeners: {
            render: me.addTooltip,
          },
        },
        {
          xtype: "textarea",
          name: "message_rx",
          fieldLabel: __("Message Pattern"),
          allowBlank: true,
        },
        {
          xtype: "gridfield",
          name: "patterns",
          fieldLabel: __("Patterns"),
          allowBlank: false,
          columns: [
            {
              text: __("Key RE"),
              dataIndex: "key_re",
              flex: 1,
              editor: "textfield",
              renderer: NOC.render.htmlEncode,
            },
            {
              text: __("Value RE"),
              dataIndex: "value_re",
              flex: 1,
              editor: "textfield",
              renderer: NOC.render.htmlEncode,
            },
          ],
        },
        {
          xtype: "gridfield",
          name: "labels",
          fieldLabel: __("Labels"),
          allowBlank: false,
          columns: [
            {
              text: __("Wildcard"),
              dataIndex: "wildcard",
              width: 200,
              editor: "textfield",
            },
            {
              dataIndex: "is_required",
              text: __("Required"),
              width: 50,
              editor: "checkbox",
              renderer: NOC.render.Bool,
            },
            {
              text: __("Set Label"),
              dataIndex: "set_label",
              width: 200,
              editor: {
                xtype: "main.label.LookupField",
              },
              renderer: NOC.render.Lookup("set_label"),
            },
            {
              text: __("Set Var"),
              dataIndex: "set_var",
              width: 100,
              editor: "textfield",
            },
          ],
        },
        {
          xtype: "gridfield",
          name: "vars",
          fieldLabel: __("Vars"),
          allowBlank: true,
          columns: [
            {
              text: __("Name"),
              dataIndex: "name",
              width: 100,
              editor: "textfield",
              renderer: NOC.render.htmlEncode,
            },
            {
              text: __("Value"),
              dataIndex: "value",
              flex: 1,
              editor: "textfield",
              renderer: NOC.render.htmlEncode,
            },
          ],
        },
        {
          name: "test_cases",
          xtype: "listform",
          rows: 3,
          fieldLabel: __("Test cases"),
          labelAlign: "top",
          items: [
            {
              xtype: "textfield",
              name: "message",
              width: 900,
              fieldLabel: __("Message"),
            },
            {
              xtype: "stringlistfield",
              name: "input_labels",
              width: 400,
              fieldLabel: __("In Labels"),
            },
            {
              xtype: "jsonfield",
              name: "raw_vars",
              fieldLabel: __("Raw Vars"),
              width: 500,
              editor: "jsonfield",
              renderer: NOC.render.JSON,
            },
          ],
        },
        // {
        //     xtype: "gridfield",
        //     name: "test_cases",
        //     fieldLabel: __("Test cases"),
        //     allowBlank: true,
        //     columns: [
        //         {
        //             text: __("Message"),
        //             dataIndex: "message",
        //             width: 200,
        //             editor: "textfield",
        //         },
        //         {
        //             text: __('Labels'),
        //             dataIndex: 'labels',
        //             width: 200,
        //             editor: 'stringlistfield'
        //         },
        //         {
        //             text: __("Raw Vars"),
        //             dataIndex: "raw_vars",
        //             flex: 1,
        //             editor: 'jsonfield',
        //             renderer: NOC.render.JSON
        //         }
        //     ]
        // }
      ],
      formToolbar: [
        {
          text: __("JSON"),
          glyph: NOC.glyph.file,
          tooltip: __("Show JSON"),
          hasAccess: NOC.hasPermission("read"),
          scope: me,
          handler: me.onJSON,
        },
        {
          text: __("Test"),
          glyph: NOC.glyph.question_circle,
          tooltip: __("Test rule"),
          hasAccess: NOC.hasPermission("test"),
          scope: me,
          handler: me.onTest,
        },
      ],
    });
    me.callParent();
  },

  onJSON: function(){
    var me = this;
    me.showItem(me.ITEM_JSON);
    me.jsonPanel.preview(me.currentRecord);
  },
  //
  onTest: function(){
    var me = this;
    me.showItem(me.ITEM_TEST_FORM);
  },
  //
  getPatterns: function(){
    var me = this;
    return me.form.getFieldValues().patterns;
  },
  getVars: function(){
    var me = this;
    return me.form.getFieldValues().vars;
  },
  //
  onCmd_from_event: function(data){
    var record = data.args,
      body = {
        id: record.id,
        source: record.get("source"),
        target: record.get("target"),
        target_id: record.get("target_id"),
        managed_object_id: record.get("managed_object_id"),
        address: record.get("address"),
        event_class_id: record.get("event_class_id"),
        message: record.get("message"),
        snmp_trap_oid: record.get("snmp_trap_oid"),
        labels: record.get("labels"),
        raw_vars: record.get("raw_vars"),
        data: record.get("data"),
        remote_id: record.get("remote_id"),
        remote_system: record.get("remote_system"),
      };
    Ext.Ajax.request({
      url: "/fm/classificationrule/from_event/" + record.id + "/",
      method: "POST",
      jsonData: body,
      scope: this,
      success: function(response){
        var model = Ext.decode(response.responseText);
        this.newRecord(model);
        if(Ext.isDefined(data.override)){
          Ext.each(data.override, function(over){
            Ext.Object.each(over, function(key, value){
              this[key] = value;
            }, this);
          }, this);
        }
      },
      failure: function(){
        NOC.error(__("Failed to create rule from event"));
      },
    });
  },
  //
  onSelectEventClass: function(combo, records){
    var me = this;
    if(!me.currentRecord){
      var name = records.get("label"),
        f = me.form.findField("name"),
        v = f.getValue();
      if(v.match(/<name>/)){
        f.setValue(v.replace("<name>", name));
      }
    }
  },
});
