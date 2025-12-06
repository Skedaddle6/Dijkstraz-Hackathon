import time
import requests
import math

#configg
API_URL = "http://localhost:9000/api/pet/update"
PET_NAME = "Tommy"
OWNER_NAME = "Jerry"
BREED = "Labrador"
HOME_LAT = 27.7172
HOME_LNG = 85.3240
SAFE_RADIUS_METERS = 100

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000 
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

def simulate_pet_movement():
    print(f"Starting Pet Tracker for {PET_NAME}...")
    
    #moving the dog
    path = [
        (0, 0), (10, 10), (30, 20), (50, 40), (80, 60), #bhitra ko radius
        (110, 80), (130, 90), (150, 100) #outside
    ]
    

    lat_per_meter = 1 / 111111
    lng_per_meter = 1 / (111111 * math.cos(math.radians(HOME_LAT)))
    
    for offset_x, offset_y in path:
        current_lat = HOME_LAT + (offset_y * lat_per_meter)
        current_lng = HOME_LNG + (offset_x * lng_per_meter)
        
        distance = calculate_distance(HOME_LAT, HOME_LNG, current_lat, current_lng)
        is_safe = distance <= SAFE_RADIUS_METERS
        
        status = "SAFE" if is_safe else "MISSING"
        print(f"📍 {PET_NAME} is at ({current_lat:.5f}, {current_lng:.5f}) - Dist: {distance:.1f}m - Status: {status}")
        
        payload = {
            "pet_name": PET_NAME,
            "owner_name": OWNER_NAME,
            "breed": BREED,
            "lat": current_lat,
            "lng": current_lng,
            "is_safe": is_safe,
            "home_lat": HOME_LAT,
            "home_lng": HOME_LNG,
            "radius": SAFE_RADIUS_METERS
        }
        
        try:
            requests.post(API_URL, json=payload)
        except Exception as e:
            print(f"Error sending update: {e}")
            
        if not is_safe:
            print(f"🚨 ALERT: {PET_NAME} has left the safe zone!")
    
            time.sleep(2)
            
        time.sleep(1)

if __name__ == "__main__":
    simulate_pet_movement()
