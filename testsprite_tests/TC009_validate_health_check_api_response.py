import requests

BASE_URL = "http://localhost:8000/api/v1/trading"
TIMEOUT = 30
HEADERS = {
    "Accept": "application/json"
}

def validate_health_check_api_response():
    url = f"{BASE_URL}/health"
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        assert isinstance(data, dict), "Response is not a JSON object"
        # Assuming health response includes keys indicating health status
        # We check for common keys like 'status' or 'health', or at least not empty
        assert data, "Health check response is empty"
    except requests.exceptions.RequestException as e:
        assert False, f"HTTP request failed: {e}"
    except ValueError:
        assert False, "Response is not valid JSON"

validate_health_check_api_response()