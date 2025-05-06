import requests
import time
from datetime import datetime

def test_api_endpoints():
    # Replace with your Render backend URL
    backend_url = "https://vehicle-tracking-backend-bwmz.onrender.com"
    detections_endpoint = f"{backend_url}/api/detections"
    telemetry_endpoint = f"{backend_url}/api/telemetry"
    detections_get_endpoint = f"{backend_url}/api/detections"

    # Current timestamp in ISO 8601 format
    current_time = datetime.utcnow().isoformat()

    # Sample telemetry data
    telemetry_data = {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "speed": 50.0,
        "timestamp": current_time
    }

    # Sample detection data (with a dummy base64 image for testing)
    detection_data = {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "speed": 50.0,
        "sign_type": "Stop",
        "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",  # Tiny 1x1 pixel image
        "timestamp": current_time
    }

    try:
        # Test POST /api/detections (telemetry)
        response = requests.post(detections_endpoint, json=telemetry_data)
        response.raise_for_status()
        data = response.json()
        expected = {"status": "success"}
        assert data == expected, f"POST telemetry expected {expected}, got {data} (Status: {response.status_code}, Response: {response.text})"
        print("POST telemetry test passed!")

        # Test POST /api/detections (detection)
        response = requests.post(detections_endpoint, json=detection_data)
        response.raise_for_status()
        data = response.json()
        assert data == expected, f"POST detection expected {expected}, got {data} (Status: {response.status_code}, Response: {response.text})"
        print("POST detection test passed!")

        # Test GET /api/telemetry
        response = requests.get(telemetry_endpoint)
        response.raise_for_status()
        data = response.json()
        assert isinstance(data, list), "GET telemetry expected a list"
        assert len(data) > 0, "GET telemetry expected non-empty list"
        assert "latitude" in data[0], "GET telemetry missing latitude"
        print("GET telemetry test passed!")

        # Test GET /api/detections
        response = requests.get(detections_get_endpoint)
        response.raise_for_status()
        data = response.json()
        assert isinstance(data, list), "GET detections expected a list"
        assert len(data) > 0, "GET detections expected non-empty list"
        assert "sign_type" in data[0], "GET detections missing sign_type"
        print("GET detections test passed!")

    except requests.RequestException as e:
        print(f"API endpoint test failed: {e} (Status: {response.status_code if 'response' in locals() else 'N/A'}, Response: {response.text if 'response' in locals() else 'No response'})")
    except AssertionError as e:
        print(f"API endpoint test failed: {e}")

if __name__ == "__main__":
    test_api_endpoints()
