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
		
		# TODO Создать тип поля, наследлованный от поля-store,
		# TODO который при создании будет добавлять в стор стандартную библиотеку виджетов,
		# TODO получая её из стора-синглтона, загружающего эту библиотеку при конструировании
		# TODO контроллера Report.controller.Root и просто хранящего её на протяжении работы интерфейса.
		# TODO Также перед синхронизацией с сервером необходимо рекорды, относящиеся к библиотеке.
		{name: 'widgets',     type: 'store', model: 'Report.model.config.Widget'}
		
		{name: 'active',      type: 'boolean'}
		{name: 'visible',     type: 'boolean'}
	]