import requests

def test_root_endpoint():
# Replace with your Render backend URL
    backend_url = "HTTPS://vehicle-tracking-backend-bwmz.onrender.com"
    try:
        response = requests.get(backend_url)
        response.raise_for_status()  # Raises an error for bad status codes
        data = response.json()
        expected = {"message": "Vehicle Tracking Backend"}
        assert data == expected, f"Expected {expected}, got {data}"
        print("Root endpoint test passed!")
    except requests.RequestException as e:
        print(f"Root endpoint test failed: {e}")
    except AssertionError as e:
        print(f"Root endpoint test failed: {e}")

if __name__ == "__main__":
    test_root_endpoint()
