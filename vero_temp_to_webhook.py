import time
import requests

def get_temperature():
    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
        temp = int(f.read()) / 1000
    return temp

def send_to_webhook(temp):
    webhook_url = 'https://webhook.url' ##Set your webhook url here
    payload = {'temperature': temp}
    response = requests.post(webhook_url, json=payload)
    return response.status_code

while True:
    temp = get_temperature()
    status = send_to_webhook(temp)
    print(f'Temperature: {temp}°C, Webhook status: {status}')
    time.sleep(10)
