###
    Модель данных конфигуратора.
###
Ext.define 'Report.model.configurator.Model',
	extend: 'Ext.data.Model'
	
	requires: [
		'Report.model.StoreField'
		'Report.model.config.Column'
		'Report.model.config.Filter'
	]
	
	fields: [
		{name: 'type',        type: 'string'}
		{name: 'name',        type: 'string'}
		{name: 'tags',        type: 'string'}
		{name: 'description', type: 'string'}
		{name: 'width',       type: 'int'   }
		{name: 'height',      type: 'int'   }
		{name: 'point',       type: 'string'}
		{name: 'columns',     type: 'store', model: 'Report.model.config.Column'}
		{name: 'filters',     type: 'store', model: 'Report.model.config.Filter'}
	]