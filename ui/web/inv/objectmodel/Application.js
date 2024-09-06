//---------------------------------------------------------------------
// inv.objectmodel application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.objectmodel.Application");

Ext.define("NOC.inv.objectmodel.Application", {
  extend: "NOC.core.ModelApplication",
  requires: [
    "NOC.core.JSONPreview",
    "NOC.core.label.LabelField",
    "NOC.core.TemplatePreview",
    "NOC.inv.objectmodel.Model",
    "NOC.inv.objectmodel.CrossDiagram",
    "NOC.inv.vendor.LookupField",
    "NOC.inv.connectiontype.LookupField",
    "NOC.inv.connectionrule.LookupField",
    "NOC.cm.configurationparam.LookupField",
    "NOC.pm.measurementunits.LookupField",
    "NOC.inv.modelinterface.LookupField",
    "NOC.inv.objectconfigurationrule.LookupField",
    "Ext.ux.form.GridField",
    "NOC.inv.facade.LookupField",
    "NOC.main.glyph.LookupField",
  ],
  model: "NOC.inv.objectmodel.Model",
  search: true,
  treeFilter: "category",
  filters: [
    {
      title: __("By Is Builtin"),
      name: "is_builtin",
      ftype: "boolean",
    },
    {
      title: __("By Vendor"),
      name: "vendor",
      ftype: "lookup",
      lookup: "inv.vendor",
    },
  ],

  actions: [
    {
      title: __("Get JSON"),
      action: "json",
      glyph: NOC.glyph.file,
      resultTemplate: new Ext.XTemplate("<pre>{data}</pre>"),
    },
  ],

  initComponent: function(){
    var me = this;

    // JSON Panel
    me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
      app: me,
      restUrl: new Ext.XTemplate("/inv/objectmodel/{id}/json/"),
      previewName: new Ext.XTemplate("Object Model: {name}"),
    });
    me.ITEM_JSON = me.registerItem(me.jsonPanel);
    // Test panel
    me.testPanel = Ext.create("NOC.core.TemplatePreview", {
      app: me,
      previewName: new Ext.XTemplate("Compatible connections for {name}"),
      template: new Ext.XTemplate(
        '<div class="noc-tp">\n    <h1>Possible connections for model {name}</h1>\n    <table border="1">\n        <tpl foreach="connections">\n            <tr>\n                <td>\n                    <tpl foreach="names">\n                        <b>{name}</b><br/><i>({description})</i><br/>\n                    </tpl>\n                </td>\n                <td>{direction}</td>\n                <td>\n                    <table>\n                        <tpl foreach="connections">\n                            <tr>\n                                <td>\n                                    <b>{name}</b><br/></i>({description})</i>\n                                </td>\n                                <td><b>{model}</b><br/>({model_description})</td>\n                            </tr>\n                        </tpl>\n                    </table>\n                </td>\n            </tr>\n        </tpl>\n    </table>\n    <h1>Internal crossing for {name}</h1>\n    <!--{grid crossing}-->\n</div>',
      ),
    });
    me.ITEM_TEST = me.registerItem(me.testPanel);
    //
    Ext.apply(me, {
      columns: [
        {
          text: __("Name"),
          dataIndex: "name",
          width: 200,
        },
        {
          text: __("Builtin"),
          dataIndex: "is_builtin",
          renderer: NOC.render.Bool,
          width: 50,
          sortable: false,
        },
        {
          text: __("Vendor"),
          dataIndex: "vendor",
          renderer: NOC.render.Lookup("vendor"),
          width: 150,
        },
        {
          text: __("Short Label"),
          dataIndex: "short_label",
          width: 150,
        },
        {
          text: __("Connection Rule"),
          dataIndex: "connection_rule",
          renderer: NOC.render.Lookup("connection_rule"),
          width: 100,
        },
        {
          text: __("CR. Context"),
          dataIndex: "cr_context",
          width: 70,
        },
        {
          text: __("Description"),
          dataIndex: "description",
          flex: 1,
        },
        {
          text: __("Labels"),
          dataIndex: "labels",
          flex: 1,
          renderer: NOC.render.LabelField,
        },
      ],
      fields: [
        {
          name: "name",
          xtype: "textfield",
          fieldLabel: __("Name"),
          allowBlank: false,
          uiStyle: "large",
        },
        {
          name: "uuid",
          xtype: "displayfield",
          fieldLabel: __("UUID"),
        },
        {
          name: "description",
          xtype: "textarea",
          fieldLabel: __("Description"),
        },
        {
          name: "vendor",
          xtype: "inv.vendor.LookupField",
          fieldLabel: __("Vendor"),
          allowBlank: false,
        },
        {
          xtype: "fieldset",
          layout: {type: "hbox"},
          title: __("Visual"),
          items: [
            {
              name: "short_label",
              xtype: "textfield",
              fieldLabel: __("Short Label"),
              allowBlank: true,
              uiStyle: "medium",
            },
            {
              name: "glyph",
              xtype: "main.glyph.LookupField",
              fieldLabel: __("Glyph"),
              allowBlank: true,
            },
          ],
        },
        {
          xtype: "fieldset",
          title: undefined,
          border: false,
          style: {
            borderTop: "none !important", // remove top border
            padding: 0,
          },
          layout: {
            type: "hbox",
          },
          items: [
            {
              name: "front_facade",
              xtype: "inv.facade.LookupField",
              fieldLabel: __("Front Facade"),
              allowBlank: true,
              listeners: {
                change: this.changeTemplateButtonState,
              },
            },
            {
              xtype: "button",
              itemId: "front_facadeBtn",
              glyph: NOC.glyph.download,
              text: __("Template"),
              margin: "0 0 0 5",
              handler: this.templateCheck,
            },
          ],
        },
        {
          xtype: "fieldset",
          title: undefined,
          border: false,
          style: {
            borderTop: "none !important", // remove top border
            padding: 0,
          },
          layout: {
            type: "hbox",
          },
          items: [
            {
              name: "rear_facade",
              xtype: "inv.facade.LookupField",
              fieldLabel: __("Rear Facade"),
              allowBlank: true,
              listeners: {
                change: this.changeTemplateButtonState,
              },
            },
            {
              xtype: "button",
              itemId: "rear_facadeBtn",
              glyph: NOC.glyph.download,
              text: __("Template"),
              margin: "0 0 0 5",
              handler: this.templateCheck,
            },
          ],
        },
        {
          name: "configuration_rule",
          xtype: "inv.objectconfigurationrule.LookupField",
          fieldLabel: __("Configuration Rule"),
          allowBlank: true,
        },
        {
          name: "connection_rule",
          xtype: "inv.connectionrule.LookupField",
          fieldLabel: __("Connection Rule"),
          allowBlank: true,
        },
        {
          name: "cr_context",
          xtype: "textfield",
          fieldLabel: __("Connection Context"),
          allowBlank: true,
          uiStyle: "medium",
        },
        {
          name: "plugins",
          xtype: "textfield",
          fieldLabel: __("Plugins"),
          allowBlank: true,
        },
        {
          name: "labels",
          xtype: "labelfield",
          fieldLabel: __("Labels"),
          allowBlank: true,
          query: {
            allow_models: ["inv.ObjectModel"],
          },
        },
        // {
        //     name: "data",
        //     xtype: "modeldatafield",
        //     fieldLabel: __("Model Data"),
        //     labelAlign: "top"
        // },
        {
          name: "data",
          fieldLabel: __("Data"),
          xtype: "gridfield",
          allowBlank: true,
          columns: [
            {
              text: __("Interface"),
              dataIndex: "interface",
              width: 150,
              editor: {
                xtype: "inv.modelinterface.LookupField",
                forceSelection: true,
                valueField: "label",
              },
            },
            {
              text: __("Key"),
              dataIndex: "attr",
              width: 150,
              editor: "textfield",
            },
            {
              text: __("Value"),
              dataIndex: "value",
              flex: 1,
              editor: "textfield",
            },
            {
              text: __("Connection"),
              dataIndex: "connection",
              flex: 1,
              editor: "textfield",
            },
            {
              text: __("Protocol"),
              dataIndex: "protocol",
              flex: 1,
              editor: "textfield",
            },
          ],
        },
        {
          name: "connections",
          xtype: "gridfield",
          fieldLabel: __("Connections"),
          columns: [
            {
              text: __("Facade"),
              dataIndex: "facade",
              width: 25,
              renderer: function(v){
                return {
                  "f": "<i class='x-btn-icon-el-default-toolbar-small fa fa-hand-o-right' title='Front'></i>",
                  "r": "<i class='x-btn-icon-el-default-toolbar-small fa fa-hand-o-left' title='Rear'></i>",
                  "": "",
                }[v];
              },
            },
            {
              text: __("Name"),
              dataIndex: "name",
              editor: "textfield",
              width: 100,
            },
            {
              text: __("Connection Type"),
              dataIndex: "type",
              editor: "inv.connectiontype.LookupField",
              width: 200,
              renderer: NOC.render.Lookup("type"),
            },
            {
              text: __("Combo"),
              dataIndex: "combo",
              editor: "textfield",
              width: 50,
            },
            {
              text: __("Cfg Ctx."),
              dataIndex: "cfg_context",
              editor: "textfield",
              width: 50,
            },
            {
              text: __("Direction"),
              dataIndex: "direction",
              editor: {
                xtype: "combobox",
                minWidth: 150,
                store: [
                  ["i", "Inner"],
                  ["o", "Outer"],
                  ["s", "Connection"],
                ],
              },
              width: 50,
              renderer: function(v){
                return {
                  i: "<i class='fa fa-arrow-down' title='" + __("Inner") + "'></i>",
                  o: "<i class='fa fa-arrow-up' title='" + __("Outer") + "'></i>",
                  s: "<i class='fa fa-arrows-h' title='" + __("Connection") + "'></i>",
                }[v];
              },
            },
            {
              text: __("Gender"),
              dataIndex: "gender",
              editor: {
                xtype: "combobox",
                minWidth: 150,
                store: [
                  ["m", "Male"],
                  ["f", "Female"],
                  ["s", "Genderless"],
                ],
              },
              width: 50,
              renderer: function(v){
                return {
                  m: "<i class='fa fa-mars' title='" + __("Male") + "'></i>",
                  f: "<i class='fa fa-venus' title='" + __("Female") + "'></i>",
                  s: "<i class='fa fa-genderless' title='" + __("Genderless") + "'></i>",
                }[v];
              },

            },
            {
              text: __("Composite"),
              dataIndex: "composite",
              width: 100,
              editor: "textfield",
            },
            {
              text: __("Composite pins"),
              dataIndex: "composite_pins",
              width: 50,
              editor: {
                xtype: "textfield",
                regex: /^\d+-\d+$/,
                regexText: __("Regex error!"),
              },
            },
            {
              text: __("Group"),
              dataIndex: "group",
              width: 100,
              editor: "textfield",
            },
            {
              text: __("Cross"),
              dataIndex: "cross_direction",
              editor: {
                xtype: "combobox",
                store: [
                  ["i", "Inner"],
                  ["o", "Outer"],
                  ["s", "Connection"],
                ],
              },
              width: 50,
            },
            {
              text: __("Protocols"),
              dataIndex: "protocols",
              width: 150,
              editor: "textfield",
            },
            {
              text: __("Internal name"),
              dataIndex: "internal_name",
              width: 150,
              editor: "textfield",
            },
            {
              text: __("Description"),
              dataIndex: "description",
              editor: "textfield",
              flex: 1,
            },
          ],
          listeners: {
            scope: me,
            clone: me.onCloneConnection,
          },
        },
        {
          xtype: "container",
          layout: {
            type: "hbox",
            align: "stretch",
          },
          itemId: "crossContainer",
          items: [
            {
              xtype: "gridfield",
              name: "cross",
              fieldLabel: __("Cross"),
              allowBlank: true,
              flex: 1,
              layout: "fit",
              columns: [
                {
                  text: __("Input"),
                  dataIndex: "input",
                  width: 150,
                  editor: {
                    xtype: "combobox",
                    valueField: "id",
                    editable: false,
                    queryMode: "local",
                    forceSelection: true,
                  },
                },
                {
                  text: __("Input Discriminator"),
                  dataIndex: "input_discriminator",
                  width: 200,
                  editor: "textfield",
                },
                {
                  text: __("Output"),
                  dataIndex: "output",
                  width: 150,
                  editor: {
                    xtype: "combobox",
                    valueField: "id",
                    editable: false,
                    queryMode: "local",
                    forceSelection: true,
                  },
                },
                {
                  text: __("Output Discriminator"),
                  dataIndex: "output_discriminator",
                  width: 200,
                  editor: "textfield",
                },
                {
                  text: __("Gain (dB)"),
                  dataIndex: "gain_db",
                  editor: "textfield",
                },
              ],
              onBeforeEdit: function(editor, context){
                if(["input", "output"].includes(context.column.dataIndex)){
                  var connectionsField = context.view
                    .up("[xtype=form]")
                    .down("[name=connections]"),
                    data = Ext.Array.map(connectionsField.value, function(value){
                      return {id: value.name, text: value.name};
                    }),
                    combo = editor.getEditor(context.record, context.column).field;
                  combo.getStore().loadData(data);
                }
                context.cancel = context.record.get("is_persist");
              },
              onCellEdit: function(editor, context){
                var me = this,
                  app = this.up("[appId=inv.objectmodel]"),
                  diagram = me.up("container").down("#diagram"),
                  ed = context.grid.columns[context.colIdx].getEditor(),
                  data = app.getFormData(),
                  padding = (diagram.config.padding || 0) * 2,
                  diagramSize = [
                    diagram.getWidth() - padding,
                    diagram.getHeight() - padding,
                  ],
                  field = context.grid.columns[context.colIdx].field;

                if(ed.rawValue){
                  context.record.set(context.field + "__label", ed.rawValue);
                }
                if(field.xtype === "labelfield"){
                  context.value = field.valueCollection.items;
                }
                if(
                  !Ext.isEmpty(context.record.get("input")) &&
                  !Ext.isEmpty(context.record.get("output"))
                ){
                  diagram.drawDiagram(data, diagramSize);
                }
              },
              onSelect: function(grid, record, index){
                var me = this;

                me.currentSelection = index;
                me.deleteButton.setDisabled(true);
                me.cloneButton.setDisabled(true);
                if(!record.get("is_persist")){
                  me.deleteButton.setDisabled(false);
                  me.cloneButton.setDisabled(false);
                }
                me.up().down("[itemId=diagram]").selectConnection(record);
              },
            },
            {
              xtype: "inv.crossdiagram",
              itemId: "diagram",
              flex: 1,
              layout: "fit",
              border: false,
              padding: 20,
              listeners: {
                resize: function(panel){
                  var app = panel.up("[appId=inv.objectmodel]"),
                    padding = (panel.config.padding || 0) * 2,
                    data = app.getFormData();

                  if(!Ext.isEmpty(data.cross)){
                    panel.drawDiagram(data, [
                      panel.getWidth() - padding,
                      panel.getHeight() - padding,
                    ]);
                  } else{
                    panel.getSurface().destroy();
                  }
                },
              },
            },
          ],
        },
        {
          name: "sensors",
          fieldLabel: __("Sensors"),
          xtype: "gridfield",
          allowBlank: true,
          columns: [
            {
              text: __("Name"),
              dataIndex: "name",
              width: 150,
              editor: "textfield",
            },
            {
              text: __("Description"),
              dataIndex: "description",
              width: 200,
              editor: "textfield",
            },
            {
              text: __("Units"),
              dataIndex: "units",
              width: 100,
              editor: "pm.measurementunits.LookupField",
              renderer: NOC.render.Lookup("units"),
            },
            {
              text: __("Modbus Register"),
              dataIndex: "modbus_register",
              width: 100,
              editor: "numberfield",
            },
            {
              text: __("Modbus Value Format"),
              dataIndex: "modbus_format",
              width: 100,
              editor: {
                xtype: "combobox",
                store: [
                  ["i16_be", "16-bit signed integer, big-endian"],
                  ["u16_be", "16-bit unsigned integer, big-endian"],
                  ["i32_be", "32-bit signed integer, big-endian"],
                  ["i32_le", "32-bit signed integer, low-endian"],
                  ["i32_bs", "32-bit signed integer, big-endian, swapped"],
                  ["i32_ls", "32-bit signed integer, low-endian, swapped"],
                  ["u32_be", "32-bit unsigned integer, big-endian"],
                  ["u32_le", "32-bit unsigned integer, low-endian"],
                  ["u32_bs", "32-bit unsigned integer, big-endian, swapped"],
                  ["u32_ls", "32-bit unsigned integer, low-endian, swapped"],
                  ["f32_be", "32-bit floating point, big-endian"],
                  ["f32_le", "32-bit floating point, low-endian"],
                  ["f32_bs", "32-bit floating point, big-endian, swapped"],
                  ["f32_ls", "32-bit floating point, low-endian, swapped"],
                ],
              },
            },
            {
              text: __("SNMP OID"),
              dataIndex: "snmp_oid",
              flex: 1,
              editor: {
                xtype: "textfield",
                vtype: "SensorOID",
              },
            },
          ],
        },
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
          glyph: NOC.glyph.question,
          tooltip: __("Test compatible types"),
          hasAccess: NOC.hasPermission("read"),
          scope: me,
          handler: me.onTest,
        },
      ],
    });
    me.callParent();
  },
  editRecord: function(record){
    this.callParent([record]);
    this.enableRearFacade(record);
  },
  //
  onJSON: function(){
    var me = this;
    me.showItem(me.ITEM_JSON);
    me.jsonPanel.preview(me.currentRecord);
  },
  //
  onTest: function(){
    var me = this;
    Ext.Ajax.request({
      url: "/inv/objectmodel/" + me.currentRecord.get("id") + "/compatible/",
      method: "GET",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText);
        me.showItem(me.ITEM_TEST).preview(me.currentRecord, data);
      },
      failure: function(){
        NOC.error(__("Failed to get data"));
      },
    });
  },
  //
  cleanData: function(v){
    var i, c, x;
    for(i in v.connections){
      c = v.connections[i];
      if(!Ext.isArray(c.protocols)){
        if(!Ext.isEmpty(c.protocols)){
          x = c.protocols.trim();
          if(x === "" || x === undefined || x === null){
            c.protocols = [];
          } else{
            c.protocols = c.protocols.split(",").map(function(v){
              return v.trim();
            });
          }
        }
      }
    }
  },
  //
  onCloneConnection: function(record){
    var v = record.get("name"),
      m = v.match(/(.*?)(\d+)/);
    if(m === null){
      return;
    }
    var n = +m[2] + 1;
    record.set("name", m[1] + n);
  },
  enableRearFacade: function(record){
    var hasRearFacade =
      Ext.Array.findBy(record.get("connections"), function(e){
        return e.direction === "o";
      }) === null
        ? true
        : false;
    this.down("button[itemId=front_facadeBtn]").setDisabled(record.get("front_facade"));
    this.down("button[itemId=rear_facadeBtn]").setDisabled(
      !hasRearFacade || record.get("rear_facade"),
    );
    this.down("field[name=rear_facade]").setDisabled(!hasRearFacade);
  },
  changeTemplateButtonState: function(field, value){
    var btn = field.up().down("button[itemId=" + field.name + "Btn]");
    btn.setDisabled(value);
  },
  templateCheck: function(btn){
    var me = this.up("[appId=inv.objectmodel]"),
      record = me.currentRecord,
      side = btn.itemId.replace("_facadeBtn", ""),
      downloadPath = Ext.String.format(
        "/inv/objectmodel/{0}/{1}/template.svg",
        record.id,
        side,
      ),
      checkPath = Ext.String.format(
        "/inv/objectmodel/{0}/is_valid_template/",
        record.id,
      );
    Ext.Ajax.request({
      url: checkPath,
      method: "GET",
      scope: me,
      success: function(response){
        var data = Ext.decode(response.responseText);
        if(data.status){
          var a = document.createElement("a");
          a.href = downloadPath;
          a.download = "";
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
        } else{
          NOC.error(__("Dimensions must be set to generate template"));
        }
      },
      failure: function(){
        NOC.error(__("Failed to get data"));
      },
    });
  },
});
