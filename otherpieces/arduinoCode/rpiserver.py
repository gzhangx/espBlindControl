

#import board
#import digitalio
import json
import time
from machine import Pin, Timer, PWM
import ggsettings

MID=1500000
MIN= 500000
MAX=2000000

def makePwm(pin):
    pwm = PWM(Pin(pin))
    pwm.freq(50)
    pwm.duty_ns(0)
    return pwm

pwmPins = {
    "GP15":makePwm(15),
    "GP14":makePwm(14),
    }
from adafruit_httpserver import HTTPServer, HTTPResponse,MIMEType

#from secrets import secrets
from pins import PinInfo


def copyControls():
    ggsettings.controls = list(map(lambda name:{ "name":name, "ctlType":"servo"},list(pwmPins.keys())))
    
# init all gpio pins to INPUT state and store in a dict mapped by id
pins = {}


# handle LED separately from the other pins - it's always an output and it's not
# really a pin (it's actually connected to the wifi module and not the main
# chip)
led = Pin("LED", Pin.OUT)

# connect to wifi


# http server
server = HTTPServer()


@server.route("/")
def base(request):
    print("root request")
    return HTTPResponse(filename="/index.html")


@server.route("/pico.svg")
def svg(request):
    # TODO: set headers so that this is cached by the browser. It's a large file
    # and takes a long time to load from the pi. Since it doesn't change much
    # (ever), don't re-transfer it on every page load.
    return HTTPResponse(filename="/pico.svg")

class CoreResponse(HTTPResponse):
    def _send_response(self, conn, status, content_type, body):
        self._send_bytes(
            conn, (
        "HTTP/1.1 200\r\n"
        "Content-Type: {}\r\n"
        "Connection: close\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "Access-Control-Allow-Headers: Content-Type,Content-Length\r\n"
        "Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n"
        "\r\n"
    ).format(MIMEType.APP_JSON)
        )
        self._send_bytes(conn, body)
        
@server.route("/update", method="OPTIONS")
def updateOptions(request):
    return CoreResponse(body="done")


def doServoOps(id, deg):
    rev = int(deg*(MAX-MIN)/100 + MIN)
    if deg < 0:
        rev = 0
    if deg > 100:
        rev = 0
    print("using deg " + str(rev)+" " + str(deg))
    pwmPins[id].duty_ns(rev)
            
@server.route("/update", method="POST")
def update(request):
    print("dbgrm rquest data " + request.request_data)
    ur = json.loads(request.request_data)
    
    if ur.get("type") == "servo":
        try:
            deg = int(ur.get("deg"))
            doServoOps(ur.get("id"), deg)            
        except Exception as e:
            print(e)
        return HTTPResponse(body="done")
    
    #pin = Pin(ur['id'], Pin.IN if ur[
    #    'inout'] == 'IN' else Pin.OUT)
        
    #if ur['id'] == 'LED' or ur['inout'] == 'OUT' and ur["type"] != "PWM":
    #    if ur['value']:            
    #        pin.on()
    #    else:            
    #        pin.off()

    return HTTPResponse(body="Unknown type " + str(ur.get("type")))


@server.route("/pinstates")
def pinstates(request):
    states = {}
    for pinID, pin in pins.items():
        pinStat = {
            "id": pinID,
            "inout":
            'In' ,
            "value": pin.value(),
        }
        if pwmPins[pinID]:
            pinState.input = 'PWM'
        states[pinID] = pinStat
    return HTTPResponse(content_type="application/json",
                        body=json.dumps(states))


@server.route("/pininfo")
def pininfo(request):
    return HTTPResponse(content_type="application/json",
                        body=json.dumps(PinInfo))


# Never returns
#server.serve_forever()
