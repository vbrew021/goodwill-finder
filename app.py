from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

SHOPGOODWILL_API = "https://buyerapi.shopgoodwill.com/api/Search/ItemListing"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
    "Origin": "https://shopgoodwill.com",
    "Referer": "https://shopgoodwill.com/",
    "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Android"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
}

DEFAULT_PAYLOAD = {
    "categoryId": "0",
    "searchText": "",
    "sortColumn": "1",
    "sortDescending": True,
    "pageSize": 40,
    "page": 1,
    "savedSearchId": 0,
    "useBuyerPrefs": False,
    "showOnlyTimeLeft": False,
    "isFromGetItems": False,
    "isFromNewSearch": True,
    "seller": "",
    "condition": [],
    "shipCountry": "US",
    "sellerState": "",
    "sellerCity": "",
    "sellerZip": "",
    "miles": 0,
    "minPrice": 0,
    "maxPrice": 0,
}

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/debug", methods=["GET"])
def debug():
    payload = {**DEFAULT_PAYLOAD, "searchText": "lego", "pageSize": 3}
    try:
        session = requests.Session()
        # First visit the homepage to get cookies
        session.get("https://shopgoodwill.com/", headers={
            "User-Agent": HEADERS["User-Agent"],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }, timeout=10)
        resp = session.post(SHOPGOODWILL_API, json=payload, headers=HEADERS, timeout=15)
        raw_text = resp.text[:2000]
        return jsonify({"status_code": resp.status_code, "raw_text": raw_text})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/search", methods=["POST"])
def search():
    body = request.get_json(silent=True) or {}
    keyword = body.get("keyword", "").strip()
    page = body.get("page", 1)
    page_size = body.get("pageSize", 40)

    if not keyword:
        return jsonify({"error": "keyword is required"}), 400

    payload = {**DEFAULT_PAYLOAD, "searchText": keyword, "page": page, "pageSize": page_size}

    try:
        session = requests.Session()
        session.get("https://shopgoodwill.com/", headers={
            "User-Agent": HEADERS["User-Agent"],
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }, timeout=10)
        resp = session.post(SHOPGOODWILL_API, json=payload, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return jsonify(data)
    except requests.exceptions.Timeout:
        return jsonify({"error": "ShopGoodwill API timed out"}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e), "status_code": getattr(e.response, "status_code", None)}), 502
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
