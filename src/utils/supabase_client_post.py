import requests, os
import time
supabase_url = os.getenv("SUPABASE_URL")
supbase_api_key = os.getenv("SUPABASE_API_KEY")
supabase_jwt = os.getenv("SUPABASE_JWT")


def log_into_supabase(data, table_name="order_groups"):
    
    url = f"{supabase_url}/rest/v1/{table_name}"
    headers = {
        "apikey": supbase_api_key,
        "Authorization": f"Bearer {supabase_jwt}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code in (200, 201):
        print("✅ Successfully logged data:", response.json())
        return response.json()
    else:
        print(f"❌ Failed to log data ({response.status_code}): {response.text}")
        return {"error": response.text, "status_code": response.status_code}

