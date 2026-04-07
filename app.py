"""
NiftyEdge — Kite API Proxy
Deploy on Railway as a Web Service
"""
import os, requests
from flask import Flask, request, Response, jsonify

app = Flask(__name__)
KITE_BASE = "https://api.kite.trade"

SKIP_HEADERS = {'host', 'content-length', 'transfer-encoding', 'connection'}

def proxy_request(method, path):
    url = KITE_BASE + path
    headers = {k: v for k, v in request.headers if k.lower() not in SKIP_HEADERS}
    try:
        resp = requests.request(
            method=method,
            url=url,
            headers=headers,
            data=request.get_data(),
            params=request.args,
            timeout=15,
            allow_redirects=False
        )
        response = Response(resp.content, status=resp.status_code)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization, X-Kite-Version, Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
        response.headers['Content-Type'] = resp.headers.get('Content-Type', 'application/json')
        return response
    except requests.exceptions.Timeout:
        return jsonify({"status": "error", "message": "Kite API timeout"}), 504
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 502

@app.route('/health')
def health():
    return jsonify({"status": "ok", "service": "NiftyEdge Kite Proxy"})

@app.route('/', defaults={'path': ''}, methods=['GET','POST','DELETE','OPTIONS'])
@app.route('/<path:path>', methods=['GET','POST','DELETE','OPTIONS'])
def catch_all(path):
    if request.method == 'OPTIONS':
        r = Response()
        r.headers['Access-Control-Allow-Origin'] = '*'
        r.headers['Access-Control-Allow-Headers'] = 'Authorization, X-Kite-Version, Content-Type'
        r.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
        return r, 200
    return proxy_request(request.method, '/' + path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
