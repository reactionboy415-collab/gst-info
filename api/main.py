from fastapi import FastAPI, HTTPException, Query
import requests
import random
import string
import time

app = FastAPI()

# --- MASTER ROTATION LOGIC ---

def get_advanced_headers():
    """Generates a unique digital fingerprint for every request"""
    # Random User-Agents
    uagents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ]
    
    # Random Fake IP for Spoofing
    fake_ip = ".".join(map(str, (random.randint(1, 254) for _ in range(4))))
    
    return {
        "User-Agent": random.choice(uagents),
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.mastersindia.co/",
        "Origin": "https://www.mastersindia.co",
        "X-Forwarded-For": fake_ip,
        "X-Real-IP": fake_ip,
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site"
    }

def generate_session_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))

# --- ENDPOINTS ---

@app.get("/")
def home():
    return {"status": "Online", "service": "GST Intel Engine"}

@app.get("/CHIRAGX9/{gstin}")
def fetch_gst_data(gstin: str, fy: str = None):
    # Fully Default Logic: If 'fy' is missing in URL, use 2025-26
    final_fy = fy if fy else "2025-26"
    
    # URL Construction
    search_url = f"https://blog-backend.mastersindia.co/api/v1/custom/search/gstin/?keyword={gstin.upper()}&unique_id={generate_session_id()}"
    status_url = f"https://blog-backend.mastersindia.co/api/v1/custom/search/gst_return_status/?keyword={gstin.upper()}&financial_year={final_fy}"
    
    headers = get_advanced_headers()

    try:
        # Step 1: Search GST Details
        response = requests.get(search_url, headers=headers, timeout=12)
        
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("success"):
                raw = res_json["data"]
                addr = raw['pradr']['addr']
                
                # Step 2: Fetch Return Status (Dynamic or Default)
                return_history = []
                try:
                    # Small delay to mimic human behavior
                    time.sleep(random.uniform(0.3, 0.7))
                    ret_res = requests.get(status_url, headers=headers, timeout=8)
                    if ret_res.status_code == 200:
                        ret_data = ret_res.json()
                        if ret_data.get("success"):
                            return_history = ret_data["data"].get("EFiledlist", [])
                except:
                    return_history = "Data Source Temporarily Unavailable"

                # Step 3: Response Construction (No Credits)
                return {
                    "success": True,
                    "gstin": gstin.upper(),
                    "selected_fy": final_fy,
                    "info": {
                        "legal_name": raw.get('lgnm'),
                        "trade_name": raw.get('tradeNam'),
                        "status": raw.get('sts'),
                        "registration_date": raw.get('rgdt'),
                        "gst_type": raw.get('dty'),
                        "address": {
                            "building": addr.get('bnm'),
                            "location": addr.get('loc'),
                            "city": addr.get('dst'),
                            "state": addr.get('stcd'),
                            "pincode": addr.get('pncd')
                        },
                        "business_nature": raw.get('nba', []),
                        "filing_history": return_history
                    }
                }
            
            return {"success": False, "message": "GSTIN not found or invalid."}
            
        elif response.status_code == 429:
            return {"success": False, "message": "Rate limit exceeded. Try again later."}
            
        raise HTTPException(status_code=response.status_code, detail="External Source Error")

    except Exception as e:
        return {"success": False, "error": str(e)}
