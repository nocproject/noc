###
	Модель источника данных для отчета.
###
Ext.define 'Report.model.wellspring.List',
	extend: 'Ext.data.Model'

	fields: [
		{name: 'id',      type: 'string'}
		{name: 'name',    type: 'string'}
		{name: 'columns', type: 'store', model: 'Report.model.config.Column'}
	]