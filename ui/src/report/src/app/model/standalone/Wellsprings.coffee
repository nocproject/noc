###
    Общедоступное хранилище источников данных.
###
Ext.define 'Report.model.standalone.Wellsprings',
	singleton: true
	
	model: 'Report.model.wellspring.List'
	proxy: 'memory'
	autoLoad: true