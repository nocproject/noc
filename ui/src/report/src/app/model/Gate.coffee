###
    Синглтон общения с сервером.
###
Ext.define 'Report.model.Gate',
	singleton: true
	
	###
        Отправка запроса на сервер.
        @param {String} point Точка доступа.
        @param {Object/Null} data Данные.
        @param {Function} next
        Следующий шаг, принимающий первым параметром результат в виде объекта.
	###
	send: (point, data, next) ->
		Ext.create 'Ext.data.Connection',
			url: '/bi'
			method: 'POST'
			jsonData:
				jsonrpc: '2.0'
				id: 0
				method: point
				params: data
			
			success: (result) ->
				result = Ext.JSON.decode result.responseBody
				
				next result.result
			
			failure: (response) ->
				Ext.Msg.show {
					title: 'Ошибка запроса к серверу'
					message: "Поинт - #{point},\n Cтатус - #{response.status}"
					buttons: Ext.Msg.YES
					icon: Ext.Msg.ERROR
				}