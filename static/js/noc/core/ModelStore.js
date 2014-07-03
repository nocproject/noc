//---------------------------------------------------------------------
// NOC.core.ModelStore
//---------------------------------------------------------------------
// Copyright (C) 2007-2012 The NOC Project
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
                },
                listeners: {
                    exception: {
                        scope: me,
                        fn: me.onSyncException
                    }
                }
            }),
            modelName = config.model + "-sm",
            sModel = Ext.define(modelName, {
                extend: "Ext.data.Model",
                fields: fields,
                proxy: proxy,
                idProperty: model.idProperty
            });

        me.idProperty = model.idProperty;
        Ext.apply(config, {
            model: sModel,
            defaultValues: defaultValues,
            storeId: config.model,
            proxy: proxy,
            syncConfig: {}
        });
        me.callParent([config]);
        me.on("write", me.onSyncWrite, me);
    },

    setFilterParams: function(config) {
        var me = this;
        me.filterParams = Ext.Object.merge({}, config);
        // Forcefully go to first page
        me.currentPage = 1;
    },

    getOpConfig: function(config) {
        var me = this;
        return Ext.apply({
                params: Ext.apply({}, me.filterParams),
                callback: function(records, operation, success) {
                    if(!success)
                        NOC.error("Failed to fetch data!");
                }
            }, config);
    },

    prefetch: function(config) {
        var me = this;
        me.callParent([me.getOpConfig(config)]);
    },

    // override sync()
    sync: function(config) {
        var me = this,
            conf = config || {};
        me.syncConfig = Ext.Object.merge({}, conf);
        if(!me.getNewRecords().length && !me.getUpdatedRecords().length
            && !me.getRemovedRecords().length) {
            // No changed records, call success callback
            Ext.callback(me.syncConfig.success,
                me.syncConfig.scope || me);
        } else {
            // Having changed records. Start sync process
            me.callParent();
        }
    },
    onSyncWrite: function() {
        var me = this;
        Ext.callback(me.syncConfig.success,
            me.syncConfig.scope || me);
    },
    onSyncException: function(proxy, response, op, opts) {
        var me = this,
            status = {
                status: response.status,
                message: response.responseText
            };
        Ext.callback(me.syncConfig.failure,
            me.syncConfig.scope || me, [response, op, status]);
    }
});
