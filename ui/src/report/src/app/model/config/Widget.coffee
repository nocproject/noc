###
	Модель конфигурации виджета.
###
Ext.define 'Report.model.config.Widget',
	extend: 'Ext.data.Model'

	fields: [
		{name: 'id',          type: 'string'}
		{name: 'name',        type: 'string'}
		{name: 'tags',        type: 'string'}
		{name: 'description', type: 'string'}
		{name: 'type',        type: 'string'}
		{name: 'wellspring',  type: 'string'}
		{name: 'columns',     type: 'store', model: 'Report.model.config.Column'}
		{name: 'filters',     type: 'store', model: 'Report.model.config.Filters'}
		{name: 'width',       type: 'int'}
		{name: 'height',      type: 'int'}
	]