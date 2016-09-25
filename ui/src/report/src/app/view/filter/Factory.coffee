###
	Синглтон-фабрика, создающая массив из виджетов, которые необходимо добавить
###
Ext.define 'Report.view.filter.Factory',
	singleton: true
	
	###
        Создание фильтра по конфигурации.
        Поля фильтров получают свойство filterSign, хранящее в себе поле num,
        указывающее на порядковый номер поля в составе фильтра, поле type,
        хранящее тип фильтра и поле model, хранящее модель конфигурации фильтра.
        @param {Report.model.config.Filter} model Модель конфигурации фильтра.
        @return {Ext.Component[]} Массив из компонентов фильтра.
	###
	makeFilter: (model) ->
		type = model.get 'type'
		
		switch type
			when 'eq'
				suffix = '='
				composition = 1
			when 'gt'
				suffix = '>'
				composition = 1
			when 'gte'
				suffix = '> или ='
				composition = 1
			when 'lt'
				suffix = '<'
				composition = 1
			when 'lte'
				suffix = '< или ='
				composition = 1
			when 'btw'
				suffix = 'между'
				composition = 2
				
		label = "#{model.get 'title'} #{suffix}"
		
		switch model.get 'type'
			when 'date'
				xtype = 'datefield'
			else
				xtype = 'textfield'
		
		result = [
			{
				xtype: 'tbtext'
				text: label
			}
		]
				
		for num in [0...composition]
			result.push {
				xtype: xtype
				filterSing: {
					num
					type
					model
				}
			}
			
		result