from machine import Pin, Timer
import network
import socket
import time
import rpiserver
import ujson
import json
import ggsettings

import utime
import urequests;

ggsettings.init()

DOWIFI = True

baseUrl ='unknown'
led = Pin("LED", Pin.OUT)
tim = Timer()
ledCounter = 0
def tick(timer):
    global led
    global ledCounter
    ledCounter = ledCounter+1;
            
    if ledCounter == 0:
        led.on()
    if ledCounter == 1:
        led.off()
    if ledCounter == 2:
        led.on()
    if ledCounter == 3:
        led.off()
    if ledCounter == 4:
        led.on()
    if ledCounter >= 10:
        led.off()
        ledCounter = -1

tim.init(period=1050, mode=Timer.PERIODIC, callback=tick)
tim.deinit()
led.off()
def ledFlash(period):
    #led.toggle()
    tim.deinit()
    tim.init(period=period, mode=Timer.PERIODIC, callback=tick)    

def doFlash(num, delay):
    for i in range(0, num):
        led.on()
        utime.sleep(delay*1.0/1000)
        led.off()
        utime.sleep(0.1)

doFlash(1,50)

def ap_mode(ssid, password):
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password)
    ap.active(True)
    while ap.active() == False:
        pass
    print("Access point active")
    print(ap.ifconfig())
    #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #creating socket object
    #s.bind(('', 80))
    #s.listen(5)
    

def connect_mode(ssid, password):
    doFlash(3,200)    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    networks = wlan.scan() # list with tuples (ssid, bssid, channel, RSSI, security, hidden)
    networks.sort(key=lambda x:x[3],reverse=True) # sorted on RSSI (3)
    for i, w in enumerate(networks):
      print(i+1, w[0].decode(), w[1], w[2], w[3], w[4], w[5])
    doFlash(1,500)    
    print("connect " + ssid+":"+password)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        doFlash(5,400)
    print(wlan.ifconfig())
    doFlash(4,100)    
    return wlan.ifconfig()

ifCfg = None
name = None
doFlash(10,10)

if DOWIFI:
    with open('secrets.json') as sec_file:
        data = ujson.load(sec_file)
        name = data["name"]
        baseUrl = data["ccSrv"]
        print(data,data['ssid'],data['password'],baseUrl)
        doFlash(3,200)
        ifCfg = connect_mode(data['ssid'],data['password'])
        doFlash(3,200)
#ap_mode("PicoW", "123456789")

if DOWIFI:
    ggsettings.name = name
    print("ifCfg", ifCfg)
    ipAddress = ifCfg[0]
    print(ipAddress,'if0')
    ggsettings.ipAddress = ipAddress
    rpiserver.copyControls()

    print("sending name ",name)
    reqbody=json.dumps({"ip":ggsettings.ipAddress,"name":ggsettings.name,
                        "controls":ggsettings.controls})
    print("reqbody",reqbody)
    doFlash(2,1000)
    while True:
        try:
            res = urequests.post(url=baseUrl+'/registerBlinds', headers = {'content-type': 'application/json'},data=reqbody)
            print("reqbody sent")
            res.close()
            break
        except:
            print("reqbody error")
            doFlash(3,1500)
            continue

    doFlash(3,100)
    print("get blinds req")
    for i in range(1):
        url = baseUrl+'/getBlinds?ip='+ipAddress+"&id="+str(i)
        print("request " ,i)
        #res = urequests.get(url)

        #print(res.text,"text")
        #jdata = json.loads(res.text)
        #print(i, jdata) #jdata['some']
        #res.close()

led.off()
ledFlash(200)
#ap_mode('ggssid','123456789')
if DOWIFI:
    rpiserver.server.serve_forever()