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
                        "business_nature": raw['nba']
                    }
                }
            return {"success": False, "message": "GSTIN not found or invalid."}
        
        raise HTTPException(status_code=response.status_code, detail="Upstream API Error")

    except Exception as e:
        return {"success": False, "error": str(e)}
