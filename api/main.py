from fastapi import FastAPI, Header, HTTPException
import requests
import random
import string

app = FastAPI()

def generate_session_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))

@app.get("/")
def read_root():
    return {"status": "Online", "owner": "CHIRAGX9", "service": "GST Intelligence API"}

@app.get("/CHIRAGX9/{gstin}")
def get_gst_api(gstin: str):
    # MastersIndia Endpoint Bypass
    url = f"https://blog-backend.mastersindia.co/api/v1/custom/search/gstin/?keyword={gstin}&unique_id={generate_session_id()}"
    
    # URL for the new Return Status feature
    return_status_url = f"https://blog-backend.mastersindia.co/api/v1/custom/search/gst_return_status/?keyword={gstin}&financial_year=2025-26"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://www.mastersindia.co/",
        "Origin": "https://www.mastersindia.co"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            res = response.json()
            if res.get("success"):
                # 🔱 Overpowered Clean JSON Response
                raw = res["data"]
                addr = raw['pradr']['addr']
                
                # --- New Addition: Fetch Return Status without changing existing logic ---
                return_data = []
                try:
                    ret_response = requests.get(return_status_url, headers=headers, timeout=5)
                    if ret_response.status_code == 200:
                        ret_res = ret_response.json()
                        if ret_res.get("success"):
                            return_data = ret_res["data"]["EFiledlist"]
                except:
                    return_data = "Source Unavailable"

                return {
                    "success": True,
                    "developer": "@dex4dev",
                    "data": {
                        "legal_name": raw['lgnm'],
                        "trade_name": raw['tradeNam'],
                        "status": raw['sts'],
                        "constitution": raw['ctb'],
                        "registration_date": raw['rgdt'],
                        "gst_type": raw['dty'],
                        "last_updated": raw['lstupdt'],
                        "address": {
                            "building": addr['bnm'],
                            "location": addr['loc'],
                            "city": addr['dst'],
                            "state": addr['stcd'],
                            "pincode": addr['pncd']
                        },
                        "jurisdiction": {
                            "state": raw['stj'],
                            "center": raw['ctj']
                        },
                        "business_nature": raw['nba'],
                        "return_status_history": return_data  # 🚂 Added at the end
                    }
                }
            return {"success": False, "message": "GSTIN not found or invalid."}
        
        raise HTTPException(status_code=response.status_code, detail="Upstream API Error")

    except Exception as e:
        return {"success": False, "error": str(e)}
