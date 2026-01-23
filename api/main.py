from fastapi import FastAPI, HTTPException, Query, Response
import httpx
import random
import string

app = FastAPI()

def generate_session_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 13)",
    "Accept": "application/json",
    "Referer": "https://www.mastersindia.co/",
    "Origin": "https://www.mastersindia.co"
}

@app.get("/")
async def root():
    return {
        "status": "Online",
        "owner": "CHIRAGX9",
        "service": "GST Intelligence API"
    }

@app.get("/CHIRAGX9/{gstin}")
async def get_gst(
    gstin: str,
    response: Response,
    fy: str = Query("2025-26", regex=r"^\d{4}-\d{2}$")
):
    # 🔒 Disable Vercel Cache
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    gst_url = (
        "https://blog-backend.mastersindia.co/api/v1/custom/search/gstin/"
        f"?keyword={gstin}&unique_id={generate_session_id()}"
    )

    return_url = (
        "https://blog-backend.mastersindia.co/api/v1/custom/search/gst_return_status/"
        f"?keyword={gstin}&financial_year={fy}"
    )

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            gst_res = await client.get(gst_url, headers=HEADERS)
            if gst_res.status_code != 200:
                raise HTTPException(502, "Upstream GST service error")

            gst_json = gst_res.json()
            if not gst_json.get("success"):
                return {"success": False, "message": "GSTIN not found or invalid"}

            raw = gst_json["data"]
            addr = raw["pradr"]["addr"]

            # Return status (optional)
            return_history = []
            try:
                ret_res = await client.get(return_url, headers=HEADERS, timeout=5)
                if ret_res.status_code == 200:
                    ret_json = ret_res.json()
                    if ret_json.get("success"):
                        return_history = ret_json["data"].get("EFiledlist", [])
            except:
                return_history = "Unavailable"

            return {
                "success": True,
                "financial_year": fy,
                "developer": "@dex4dev",
                "data": {
                    "legal_name": raw["lgnm"],
                    "trade_name": raw["tradeNam"],
                    "status": raw["sts"],
                    "constitution": raw["ctb"],
                    "registration_date": raw["rgdt"],
                    "gst_type": raw["dty"],
                    "last_updated": raw["lstupdt"],
                    "address": {
                        "building": addr["bnm"],
                        "location": addr["loc"],
                        "city": addr["dst"],
                        "state": addr["stcd"],
                        "pincode": addr["pncd"]
                    },
                    "jurisdiction": {
                        "state": raw["stj"],
                        "center": raw["ctj"]
                    },
                    "business_nature": raw["nba"],
                    "return_status_history": return_history
                }
            }

        except httpx.TimeoutException:
            raise HTTPException(504, "Request timed out")
        except Exception as e:
            return {"success": False, "error": str(e)}
