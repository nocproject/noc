Ext.define 'Report.model.Library',
	extend: 'Ext.data.Model'

	fields: [
		{name: 'id',          type: 'int'   }
		{name: 'name',        type: 'string'}
		{name: 'description', type: 'string'}
		{name: 'groupId',     type: 'int'   }
		{name: 'groupName',   type: 'string'}
	]
