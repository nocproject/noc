//---------------------------------------------------------------------
// sa.discoveredobject application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.discoveredobject.model.Container");

Ext.define("NOC.sa.discoveredobject.model.Container", {
    extend: "Ext.app.ViewModel",
    alias: "viewmodel.sa.discoveredobject.container",

    data: {
        isFilterOpen: true,
    },
    formulas: {
        buttonDisabled: {
            bind: {
                isNotSelectedRow: "{sa-discoveredobject-grid.selection}",
                filter: "{sa-discovered-sidebar.value}",
            },
            get: function(data) {
                var isEmpty = true;

                Ext.Object.each(data.filter, function(_, value) {
                    if(!Ext.isEmpty(value)) {
                        isEmpty = false;
                        return false;
                    }
                });

                return Ext.isEmpty(data.isNotSelectedRow) && isEmpty;
            }
        }
    },
});