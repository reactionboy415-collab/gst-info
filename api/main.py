from fastapi import FastAPI, HTTPException, Query
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

@app.get("/CHIRAGX9/{gstin}")
async def get_gst(
    gstin: str,
    fy: str = Query("2025-26", regex=r"^\d{4}-\d{2}$")
):
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

            data = gst_res.json()
            if not data.get("success"):
                return {"success": False, "message": "Invalid GSTIN"}

            raw = data["data"]
            addr = raw["pradr"]["addr"]

            # Return Status
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
                "data": {
                    "legal_name": raw["lgnm"],
                    "trade_name": raw["tradeNam"],
                    "status": raw["sts"],
                    "registration_date": raw["rgdt"],
                    "return_status_history": return_history
                }
            }

        except httpx.TimeoutException:
            raise HTTPException(504, "Request timed out")
