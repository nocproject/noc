###
	Модель конфигурации корневой секции всей конфигурации.
###
Ext.define 'Report.model.config.Root',
	extend: 'Ext.data.Model'

	requires: [
		'Report.model.StoreField'
		'Report.model.config.Dashboard'
	]
	
	fields: [
		{name: 'version',    type: 'string'}
		{name: 'dashboards', type: 'store', model: 'Report.model.config.Dashboard'}
	]