import time
import random
import requests
import json

# Configg
API_URL = "http://localhost:9000/api/iot/noise"
DEVICE_ID = "iot-mic-001"
LAT = 27.7172  # kathmandu ko
LNG = 85.3240
THRESHOLD_DB = 50  # for now as 50db is good to test on laptop

def simulate_noise_monitoring():
    print(f"Starting IoT Noise Monitor (Device: {DEVICE_ID})")
    print(f"Monitoring for noise levels > {THRESHOLD_DB} dB...")
    
    while True:
        #we r simulating noise levels (random value between 10 and 100)
        #irl, this coudl be from a microphone
        current_db = random.uniform(10, 60)
        
        print(f"Current Noise Level: {current_db:.2f} dB")
        
        if current_db > THRESHOLD_DB:
            print(f"⚠️ High noise detected! Sending alert...")
            send_alert(current_db)
            #waiting some time
            time.sleep(10) 
        
        time.sleep(2)

def send_alert(db_level):
    payload = {
        "device_id": DEVICE_ID,
        "noise_level": db_level,
        "lat": LAT,
        "lng": LNG,
        "timestamp": time.time()
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            print("✅ Alert sent successfully!")
            print(f"Server Response: {response.json()}")
        else:
            print(f"❌ Failed to send alert. Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error sending alert: {e}")

if __name__ == "__main__":
    try:
        simulate_noise_monitoring()
    except KeyboardInterrupt:
        print("\nStopping IoT Monitor...")
