from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

SHOPGOODWILL_API = "https://buyerapi.shopgoodwill.com/api/Search/ItemListing"

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
}

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Origin": "https://shopgoodwill.com",
    "Referer": "https://shopgoodwill.com/",
}

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/debug", methods=["GET"])
def debug():
    payload = {**DEFAULT_PAYLOAD, "searchText": "lego", "pageSize": 3}
    try:
        resp = requests.post(SHOPGOODWILL_API, json=payload, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return jsonify({"status": "ok", "raw": data})
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
        resp = requests.post(SHOPGOODWILL_API, json=payload, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return jsonify(data)
    except requests.exceptions.Timeout:
        return jsonify({"error": "ShopGoodwill API timed out"}), 504
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
