# ===== IMPORT =====
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

# ===== LOAD ENV =====
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE = os.getenv("TABLE")

# Validasi ENV
if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERROR: SUPABASE_URL atau SUPABASE_KEY tidak ditemukan di .env!")
else:
    print(f"✅ Terhubung ke Supabase: {SUPABASE_URL}")

BASE_URL = f"{SUPABASE_URL}/rest/v1/{TABLE}"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# ===== INIT APP =====
app = FastAPI(title="API Mahasiswa Supabase")

# ===== CORS SETTINGS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Mengizinkan akses dari mana saja (termasuk file HTML lokal)
    allow_credentials=True,
    allow_methods=["*"],      # Mengizinkan semua method (GET, POST, PUT, DELETE)
    allow_headers=["*"],
)

# Tambahkan middleware untuk debugging print
@app.middleware("http")
async def log_requests(request, call_next):
    print(f"DEBUG: Request {request.method} ke {request.url.path}")
    response = await call_next(request)
    if response.status_code >= 400:
        print(f"DEBUG: Response error {response.status_code}")
    return response

# ===== MODEL =====
class Mahasiswa(BaseModel):
    nama: str
    nim: str
    jurusan: str

# ===== HELPER UNTUK HANDLING RESPON =====
def safe_response(r):
    try:
        # Supabase sering mengembalikan status 204 (No Content) atau 201 dengan isi
        if r.status_code == 204:
            return {"message": "Operation successful, no content returned"}
        if r.text and r.text.strip():
            return r.json()
        return {"message": "success", "status": r.status_code}
    except:
        return {"raw": r.text}


# ===== ROUTES =====

# ROOT
@app.get("/")
def root():
    return {"message": "API berjalan"}

# GET DATA
@app.get("/mahasiswa")
def get_mahasiswa():
    try:
        # Menambahkan timeout agar server tidak 'hang' jika koneksi internet lambat
        r = requests.get(BASE_URL, headers=headers, timeout=10)
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=f"Supabase Error: {r.text}")
        return safe_response(r)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Gagal menghubungi Supabase: {str(e)}")

# INSERT DATA
@app.post("/mahasiswa")
def create_mahasiswa(data: Mahasiswa):
    try:
        # Gunakan model_dump() untuk Pydantic v2
        r = requests.post(BASE_URL, headers=headers, json=data.model_dump(), timeout=10)
        if r.status_code not in [200, 201]:
            # Memberikan detail error yang lebih spesifik jika RLS memblokir insert
            raise HTTPException(status_code=r.status_code, detail=f"Insert Gagal: {r.text}")
        return safe_response(r)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

# UPDATE DATA
@app.put("/mahasiswa/{id}")
def update_mahasiswa(id: str, data: Mahasiswa):
    url = f"{BASE_URL}?id=eq.{id}"

    r = requests.patch(url, headers=headers, json=data.model_dump())

    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    return safe_response(r)

# DELETE DATA
@app.delete("/mahasiswa/{id}")
def delete_mahasiswa(id: str):
    url = f"{BASE_URL}?id=eq.{id}"

    r = requests.delete(url, headers=headers)

    if r.status_code != 200:
        raise HTTPException(status_code=r.status_code, detail=r.text)

    return {"message": "deleted"}