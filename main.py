from machine import Pin, PWM
import network
import time
import urequests
import ujson
from utime import sleep
from neopixel import NeoPixel
import _thread

#from firebase_admin import db
#import RPi.GPIO as GPIO

servo = PWM(Pin(7))
servo.freq(50)

red_pin = Pin(16, Pin.OUT)   # 빨간색 LED를 연결한 핀 번호
green_pin = Pin(17, Pin.OUT)

SCL_PIN = 14
SDO_PIN = 15
entered_password = ""
missCount=0

#GPIO.setup(SCL_PIN, GPIO.OUT)
#GPIO.setup(SDO_PIN, GPIO.IN)

#네오픽셀 연결할 output 핀 지정
NeoPin=Pin(13,Pin.OUT)
np=NeoPixel(NeoPin,12)

#부저 핀 설정
buzzer=PWM(Pin(18))

#버튼 핀
button_pin = Pin(15, Pin.IN, Pin.PULL_DOWN)

#충격감지센서
shock_sensor_pin = Pin(28, Pin.IN)

# WLAN 객체를 생성하고, 무선 LAN을 활성화합니다
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# 와이파이에 연결합니다
if not wlan.isconnected():
    wlan.connect("KT_GiGA_2G_GONGGAN", "ggs4310910")
    print("Waiting for Wi-Fi connection", end="...")
    while not wlan.isconnected():
        print(".", end="")
        time.sleep(1)
else:
    print(wlan.ifconfig())
    print("WiFi is Connected")

# Firebase의 Realtime Database와 연결하기 위한 URL을 설정합니다
url = "https://smart-987d3-default-rtdb.firebaseio.com/"

def firebase_get_open():
    response = urequests.get(url + "/open.json")
    time.sleep(0.1)

    try:
        data = ujson.loads(response.text)
        print("open value:", response.text)
        return data
    except ValueError as e:
        print("Error parsing JSON:", e)
    finally:
        response.close()

def firebase_get():
    response = urequests.get(url + "/password.json")
    time.sleep(0.1)

    # 텍스트 데이터를 JSON으로 파싱
    try:
        data = ujson.loads(response.text)
        print("password:", response.text)
        return data
    except ValueError as e:
        print("Error parsing JSON:", e)
    finally:
        response.close()  # 리소스 반환

def read_keypad():
    num = 0
    for i in range(1, 9):
        GPIO.output(SCL_PIN, 0)
        if GPIO.input(SDO_PIN) == 0:
            num = i
            print(num)
        GPIO.output(SCL_PIN, 1)
    return num


def move_servo():
    # 반시계방향으로 90도 돌기
    servo.duty_u16(4200)
    sleep(5)
    servo.duty_u16(1310)


    

def read_takePicture():
    response = urequests.get(url + "/picture.json")
    time.sleep(0.1)
    # 텍스트 데이터를 JSON으로 파싱
    try:
        data = ujson.loads(response.text)
        print(data)
        return data
    except ValueError as e:
        print("Error parsing JSON:", e)
    finally:
        response.close()  # 리소스 반환


def update_firebase():
    full_url ="https://smart-987d3-default-rtdb.firebaseio.com/.json"
    data = 0
    json_data = ujson.dumps(data)
    response = urequests.post(full_url, data={'picture':'0'})
    print("response: ", response)
    print("response.text: ", response.text)

        
   
def tone():
    buzzer.duty_u16(30000)
    buzzer.freq(523)
    sleep(1)
    buzzer.duty_u16(0)

def take_Picture():
    for i in range(12):
        np[i]=(255,255,255)
    np.write()
    time.sleep(10)
    
    for i in range(12):
        np[i]=(0,0,0)
    np.write()
    




while True:
    open_value = firebase_get_open()
    if open_value == "1":
        green_pin.on()
        move_servo() 
        green_pin.off()
    
    password = firebase_get()
    shock_value = shock_sensor_pin.value()
    picture=read_takePicture()
    
    if picture=="1":
        take_Picture()
        
    
    # 충격이 감지되면 빨간 LED 켜기
    if shock_value == "1":
        print("Shock detected!")
        red_pin.on()
        time.sleep(1)
        red_pin.off()# 원하는 시간 동안 LED를 켜놓거나 다른 동작을 수행할 수 있습니다.
   
    
    entered_password = input("Enter the password: ")

     # 4자리 입력되면 확인
    attempt_count = 0  # 비밀번호 실패 횟수 초기화
    while len(entered_password) == 4 and entered_password != password:
        print("Password Incorrect!")
        missCount += 1
        entered_password = ""
        attempt_count += 1
        if attempt_count >= 3:  # 두 번까지만 허용
            break
        entered_password = input("Enter the password: ")

    if len(entered_password) == 4 and entered_password == password:
        print("Password Correct!")
        green_pin.on()
        move_servo()  # 모터를 움직이는 함수 호출
        green_pin.off()

    if missCount >= 3:
        red_pin.on()
        tone()
        red_pin.off()
        missCount = 0
                
                
