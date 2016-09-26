###
	Модель произвольных запросов данных для виджета.
###
Ext.define 'Report.model.query.Query',
	extend: 'Ext.data.Model'

	fields: [
		{name: 'query', type: 'string'}
	]