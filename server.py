# ===== IMPORT LIBRARY =====
from http.server import BaseHTTPRequestHandler, HTTPServer   # untuk membuat web server sederhana
import json                                                  # untuk parsing JSON
import requests                                              # untuk request ke Supabase
import urllib.parse                                          # untuk parsing form data (optional)


# ===== KONFIGURASI SUPABASE =====
PROJECT_URL = "https://ceriexguqkkzgjzevesj.supabase.co"      # URL project Supabase kamu
TABLE = "mahasiswa"                                          # nama tabel di database
SUPABASE_URL = f"{PROJECT_URL}/rest/v1/{TABLE}"               # endpoint REST Supabase

API_KEY = "sb_publishable_YLK0y4gELq5jmzJ1izvp4w_pZki0LzL"   # gunakan publishable / anon key

# HEADER untuk komunikasi ke Supabase
headers = {
    "apikey": API_KEY,                                       # API key wajib
    "Authorization": f"Bearer {API_KEY}",                    # token authorization
    "Content-Type": "application/json",                      # tipe data JSON
    "Prefer": "return=representation"                        # agar Supabase mengembalikan data
}


# ===== FUNGSI AMAN UNTUK PARSING JSON =====
def safe_json(response):
    try:
        # cek apakah response ada isinya
        if response.text and response.text.strip():
            return response.json()                           # parse JSON jika ada isi
        else:
            # jika kosong, tetap return success
            return {
                "status": response.status_code,
                "message": "success (no content)"
            }
    except Exception as e:
        # jika gagal parsing JSON
        return {
            "status": response.status_code,
            "error": str(e),
            "raw": response.text
        }


# ===== CLASS HANDLER SERVER =====
class APIHandler(BaseHTTPRequestHandler):

    # fungsi untuk mengirim response JSON ke client
    def send_json(self, data, status=200):
        self.send_response(status)                           # set status code
        self.send_header("Content-type", "application/json") # header JSON
        self.send_header("Access-Control-Allow-Origin", "*") # Izinkan semua origin (CORS)
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()                                   # akhiri header
        self.wfile.write(json.dumps(data).encode())          # kirim data ke client

    # ===== HANDLE OPTIONS (Preflight Request untuk CORS) =====
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # ===== HANDLE GET =====
    def do_GET(self):
        try:
            print("GET:", self.path)

            # endpoint GET /mahasiswa
            if self.path == "/mahasiswa":
                r = requests.get(SUPABASE_URL, headers=headers)   # ambil data dari Supabase
                result = safe_json(r)                             # parsing aman
                self.send_json(result)                            # kirim ke client

            else:
                self.send_json({"error": "endpoint tidak ditemukan"}, 404)

        except Exception as e:
            self.send_json({"error": str(e)}, 500)


    # ===== HANDLE POST =====
    def do_POST(self):
        try:
            print("POST:", self.path)

            if self.path == "/mahasiswa":

                # ambil panjang body
                length = int(self.headers.get('Content-Length', 0))

                # baca body request
                body = self.rfile.read(length)

                # ===== parsing body =====
                if "application/json" in self.headers.get("Content-Type", ""):
                    data = json.loads(body)                   # jika JSON
                else:
                    data = urllib.parse.parse_qs(body.decode())  # jika form
                    data = {k: v[0] for k, v in data.items()}

                # mapping ke payload database
                payload = {
                    "nama": data.get("nama"),
                    "nim": data.get("nim"),
                    "jurusan": data.get("jurusan")
                }

                print("PAYLOAD:", payload)

                # kirim ke Supabase
                r = requests.post(SUPABASE_URL, headers=headers, data=json.dumps(payload))

                print("STATUS:", r.status_code)
                print("RESPONSE:", r.text)

                result = safe_json(r)   # parsing aman

                self.send_json(result)

            else:
                self.send_json({"error": "endpoint tidak ditemukan"}, 404)

        except Exception as e:
            print("ERROR:", str(e))
            self.send_json({"error": str(e)}, 500)


    # ===== HANDLE PUT (UPDATE) =====
    def do_PUT(self):
        try:
            if self.path.startswith("/mahasiswa/"):

                # ambil ID dari URL
                id = self.path.split("/")[-1]

                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length)

                data = json.loads(body)

                url = f"{SUPABASE_URL}?id=eq.{id}"

                r = requests.patch(url, headers=headers, data=json.dumps(data))

                result = safe_json(r)

                self.send_json(result)

            else:
                self.send_json({"error": "endpoint tidak ditemukan"}, 404)

        except Exception as e:
            self.send_json({"error": str(e)}, 500)


    # ===== HANDLE DELETE =====
    def do_DELETE(self):
        try:
            if self.path.startswith("/mahasiswa/"):

                id = self.path.split("/")[-1]

                url = f"{SUPABASE_URL}?id=eq.{id}"

                r = requests.delete(url, headers=headers)

                result = safe_json(r)

                self.send_json(result)

            else:
                self.send_json({"error": "endpoint tidak ditemukan"}, 404)

        except Exception as e:
            self.send_json({"error": str(e)}, 500)


# ===== MENJALANKAN SERVER =====
def run():
    server_address = ('0.0.0.0', 8000)                        # jalankan di port 8000
    httpd = HTTPServer(server_address, APIHandler)           # inisialisasi server
    print("Server running at http://localhost:8000")         # info ke user
    httpd.serve_forever()                                    # server berjalan terus


# ===== ENTRY POINT =====
if __name__ == "__main__":
    run()                                                    # jalankan server