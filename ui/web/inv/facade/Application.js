//---------------------------------------------------------------------
// inv.facade application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.facade.Application");

Ext.define("NOC.inv.facade.Application", {
    extend: "NOC.core.ModelApplication",
    requires: ["NOC.inv.facade.Model"],
    model: "NOC.inv.facade.Model",
    search: true,
    treeFilter: "category",
    initComponent: function(){
        var me = this;
        // JSON Panel
        me.jsonPanel = Ext.create("NOC.core.JSONPreview", {
            app: me,
            restUrl: new Ext.XTemplate("/inv/facade/{id}/json/"),
            previewName: new Ext.XTemplate("Facade: {name}"),
        });
        me.ITEM_JSON = me.registerItem(me.jsonPanel);
        //
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    width: 300,
                    dataIndex: "name",
                },
                {
                    text: __("Description"),
                    flex: 1,
                    dataIndex: "description",
                },
            ],
            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
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
                  
                    xtype: "filefield",
                    name: "svgFile",
                    fieldLabel: "SVG",
                    labelWidth: 50,
                    buttonText: "Select file...",
                    listeners: {
                        change: function(field){
                            var element, file,
                                elementExt = field.getEl();

                            if(!elementExt){
                                return;
                            }

                            element = elementExt.down("input[type=file]");
                            file = element.dom.files[0];

                            if(file){
                                var reader = new FileReader();

                                reader.onload = function(e){
                                    var dataField = field.up("form").down("hiddenfield[name=data]");
                                    dataField.setValue(e.target.result);
                                };

                                reader.onerror = function(){
                                    NOC.error(__("Error reading svg-file"));
                                };

                                reader.readAsText(file);
                            }
                        }
                    },
                },
                {
                    name: "data",
                    xtype: "hiddenfield",
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
            ],
        });
        me.callParent();
    },
    //
    onJSON: function(){
        var me = this;
        me.showItem(me.ITEM_JSON);
        me.jsonPanel.preview(me.currentRecord);
    },
});
