Ext.define 'Report.data.Ion',
	extend: 'Report.data.AsyncInterface'

	# Строковый идентификатор того что мы хотим от сервера
	method: ''

	# Массив параметров для сервера
	params: null

	# Какой-либо результат, либо null если ошибка
	result: null

	# Текст ошибки в случае если ошибка произошла
	error: ''

	# Успешность или не успешность запроса
	isSuccess: false

	# Находится ли ион в процессе ожидания ответа сервера
	pending: false

	# Поле для особых параметров, добавляются поверх параметров из params
	extraParams: null

	callSuccess: () ->
		@callParent [@error, @result]

	callFailure: () ->
		@callParent [@error, @result]

	callCallback: () ->
		if @isSuccess
			@callSuccess
		else
			@callFailure