###
	Модель конфигурации дашборда.
###
Ext.define 'Report.model.config.Dashboard',
	extend: 'Ext.data.Model'

	requires: [
		'Report.model.config.Filter'
		'Report.model.config.Widget'
	]
	
	fields: [
		{name: 'id',          type: 'string'}
		{name: 'name',        type: 'string'}
		{name: 'tags',        type: 'string'}
		{name: 'description', type: 'string'}
		{name: 'filters',     type: 'store', model: 'Report.model.config.Filter'}
		{name: 'widgets',     type: 'store', model: 'Report.model.config.Widget'}
		{name: 'active',      type: 'boolean'}
		{name: 'visible',     type: 'boolean'}
	]