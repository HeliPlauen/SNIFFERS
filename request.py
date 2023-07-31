import requests


x = requests.post('https://178.151.98.246:30', json={
	'action':'set_parameters',
	"miraBusinessPorts":{"tcp": [] , "udp" : [] }, 
	"nvidiaPorts" : [{"266":"656516951"}, { "995":"643346951" }] , 
	"_id" : "63e4aad7f509eb99be31186f", 
	"computerName" : "", 
	"tcpPorts" : [{"12545":"788321321"}] , 
	"udpPorts" : [{"222545":"656516951"}, { "2245":"643346951" }] , 
	"computerOwnerId" : "", 
	"computerStatus" : "", 
	"computerClass" : "", 
	"accessPort" : "", 
	"inService" : true, 
	"isVerified" : false, 
	"verificationCode" : 0, 
	"date" : "2023-02-09T08:12:07.218Z", 
	"__v" : 0, 
	"mainingStatus" : true
}, verify=False)

