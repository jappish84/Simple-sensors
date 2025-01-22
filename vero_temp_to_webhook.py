import time
import requests

def get_temperature():
    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
        temp = int(f.read()) / 1000
    return temp

def send_to_webhook(temp):
    webhook_url = 'https://webhook.url'  # Set your webhook URL here
    payload = {'temperature': temp}
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f'Error sending to webhook: {e}')
        return None

while True:
    temp = get_temperature()
    status = send_to_webhook(temp)
    if status:
        print(f'Temperature: {temp}°C, Webhook status: {status}')
    else:
        print(f'Temperature: {temp}°C, Failed to send to webhook')
    time.sleep(10)
