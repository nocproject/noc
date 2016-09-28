###
	Модель конфигурации корневой секции всей конфигурации.
###
Ext.define 'Report.model.config.Root',
	extend: 'Ext.data.Model'

	fields: [
		{name: 'version',    type: 'string'}
		{name: 'dashboards', type: 'store', model: 'Report.model.config.Dashboard'}
	]