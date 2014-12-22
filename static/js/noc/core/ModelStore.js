//---------------------------------------------------------------------
// NOC.core.ModelStore
//---------------------------------------------------------------------
// Copyright (C) 2007-2014 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.core.ModelStore");

Ext.define("NOC.core.ModelStore", {
    extend: "Ext.data.BufferedStore",
    filterParams: undefined,
    url: undefined,
    model: undefined,
    remoteSort: true,
    remoteFilter: true,
    customFields: [],
    autoLoad: false,

    constructor: function(config) {
        var me = this,
            model = Ext.create(config.model),
            fields = model.fields.items.concat(config.customFields),
            defaultValues = {};

        for(var i=0; i < fields.length; i++) {
            var field = fields[i],
                dv = field.defaultValue;
            if(dv !== undefined && dv !== "") {
                defaultValues[field.name] = dv;
            }
        }
        // Additional fields
        fields = fields.concat([
            {
                name: "fav_status",
                type: "boolean",
                persist: false
            }
        ]);
        var proxy = Ext.create("Ext.data.RestProxy", {
                url: model.rest_url,
                pageParam: "__page",
                startParam: "__start",
                limitParam: "__limit",
                sortParam: "__sort",
                extraParams: {
                    "__format": "ext"
                },
                reader: {
                    type: "json",
                    rootProperty: "data",
                    totalProperty: "total",
                    successProperty: "success"
                },
                writer: {
                    type: "json"
                }
            }),
            modelName = config.model + "-sm",
            schema = Ext.data.schema.Schema.get("default"),
            sModel = schema.getEntity(modelName);

        if(!sModel) {
            sModel = Ext.define(modelName, {
                extend: "Ext.data.Model",
                fields: fields,
                proxy: proxy,
                idProperty: model.idProperty
            });
        }

        me.idProperty = model.idProperty;
        Ext.apply(config, {
            model: sModel,
            defaultValues: defaultValues,
            storeId: config.model,
            proxy: proxy,
            syncConfig: {}
        });
        me.callParent([config]);
    },

    setFilterParams: function(config) {
        var me = this;
        me.filterParams = Ext.apply({}, config);
        // Forcefully go to first page
        me.currentPage = 1;
    },

    getOpConfig: function(config) {
        var me = this;
        return Ext.apply({
                params: Ext.apply({}, me.filterParams),
                callback: function(records, operation, success) {
                    if(!success) {
                        NOC.error("Failed to fetch data!");
                    }
                }
            }, config);
    },

    prefetch: function(config) {
        var me = this;
        config = me.getOpConfig(config);
        me.callParent([config]);
    }
});
