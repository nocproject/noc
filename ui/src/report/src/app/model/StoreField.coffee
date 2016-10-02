###
	Тип поля, хранящий в себе полноценный Ext.data.Store.
	Для работы необходимо указать в конфигурации значение для свойства model с именем класса модели,
	которая будет использоваться для разбора данных поля.
###
Ext.define 'Report.model.StoreField',
	extend: 'Ext.data.field.Field'
	alias: 'data.field.store'

	###
		@property {Boolean} reverseData
		При включении этого флага массив входных данных переворачивается наоборот,
		используя метод reverse для массивов.
	###
	reverseData: false

	###
		@property {String} model Имя модели для стора.
	###
	model: null

	###
		@inheritdoc
	###
	getType: () ->
		'store'

	###
		@inheritdoc
	###
	convert: (value) ->
		value = Ext.Array.from value

		if @reverseData
			value.reverse()

		Ext.create 'Ext.data.Store',
			model: this.model,
			data: value or []