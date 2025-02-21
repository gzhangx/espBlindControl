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
