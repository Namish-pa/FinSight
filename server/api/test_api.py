import requests

BASE_URL = "http://localhost:8000"

def main():
    print("=" * 50)
    print("FinSight API - Manual Test")
    print("=" * 50)
    
    print("\n1. GET /api/kpis")
    try:
        res_kpi = requests.get(f"{BASE_URL}/api/kpis")
        print(f"Status: {res_kpi.status_code}")
        print("Response:", res_kpi.json())
    except Exception as e:
        print(f"Error: {e}")

    print("\n2. GET /api/forecast")
    try:
        res_forecast = requests.get(f"{BASE_URL}/api/forecast")
        print(f"Status: {res_forecast.status_code}")
        print("Response:", res_forecast.json())
    except Exception as e:
        print(f"Error: {e}")

    print("\n3. POST /api/ask")
    try:
        res_ask = requests.post(f"{BASE_URL}/api/ask", json={"question": "How many invoices are overdue?"})
        print(f"Status: {res_ask.status_code}")
        print("Response:", res_ask.json())
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
