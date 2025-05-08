import requests
import time
from datetime import datetime

def ping_health():
    url = "https://vehicle-tracking-backend-bwmz.onrender.com/api/health"
    try:
        response = requests.get(url)
        print(f"[{datetime.now()}] Health check: {response.status_code}")
    except Exception as e:
        print(f"[{datetime.now()}] Error: {str(e)}")

if __name__ == "__main__":
    print("Starting health check pinger...")
    while True:
        ping_health()
        # Ping every 14 minutes to keep the service alive
        time.sleep(14 * 60) 