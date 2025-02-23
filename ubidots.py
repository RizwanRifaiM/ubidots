import network
import urequests
import ujson
import utime
from machine import Pin
import dht

SSID = "cs"
PASSWORD = ""

SERVER_URL = "http://192.168.1.6:5000/sensor"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Menghubungkan ke WiFi...")
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            utime.sleep(1)
    print("WiFi Terhubung:", wlan.ifconfig())
    
    
dht_sensor = dht.DHT11(Pin(19))
pir_sensor = Pin(23, Pin.IN)
connect_wifi()

while True:
    try:
        dht_sensor.measure()
        suhu = dht_sensor.temperature()
        kelembapan = dht_sensor.humidity()
        gerakan = pir_sensor.value()

        data = ujson.dumps({"suhu": suhu, "kelembapan": kelembapan, "gerakan": gerakan})
        headers = {'Content-Type': 'application/json'}

        response = urequests.post(SERVER_URL, data=data, headers=headers)
        print("Data terkirim : ", "suhu:",suhu,"kelembapan:",kelembapan,"gerakan:",gerakan)
        response.close()

    except Exception as e:
        print("Error mengirim data:", e)

    utime.sleep(5)
