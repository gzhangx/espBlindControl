otherpieces\prints contains 3d prints

otherpieces\arduinoCode contains raspberry pi pico code, on start up register with server, contain code to control 2 servos

blinds-web contains web code from server, copy the out to server out 

I originally want to use esp, but changed to pico instead



http://192.168.0.xxxxx:18082/getBlinds gets blinds, contains in secrets.json

{
"name":"shutter1",
"ccSrv":"http://192.168.0.xxxx:18082",
    "ssid":"xxxxxxx-low",
    "password":"xxxxxxxx"
    }


each item register with

{"shutter1":{"name":"shutter1","ip":"192.168.0.xxx","controls":[{"name":"GP15","ctlType":"servo"},{"name":"GP14","ctlType":"servo"}],"updateTime":"2025-02-21T17:16:35.288Z"}}

http://192.168.0.xxx:18082/getBlinds will return the above


POST http://192.168.0.xxx/update

{"ip":"192.168.0.xxx","id":"GP15","deg":"0","type":"servo"}
{"ip":"192.168.0.xxx","id":"GP15","deg":"90","type":"servo"}  //close