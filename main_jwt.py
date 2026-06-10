from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
import os
from dotenv import load_dotenv
from pydantic import BaseModel

# ===== INIT =====
appjwt = FastAPI(title="FastAPI + Supabase + JWT")
security = HTTPBearer()

# ===== LOAD ENV =====
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TABLE = os.getenv("TABLE")

BASE_URL = f"{SUPABASE_URL}/rest/v1/{TABLE}"

# ===== MODEL =====
class LoginRequest(BaseModel):
    email: str
    password: str

class Mahasiswa(BaseModel):
    nama: str
    nim: str
    jurusan: str


# ===== HELPER =====
def safe_json(response):
    try:
        if response.text:
            return response.json()
        return {"message": "success"}
    except:
        return {"raw": response.text}


# ===== LOGIN =====
@appjwt.post("/login")
def login(data: LoginRequest):
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"

    headers = {
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json"
    }

    r = requests.post(url, headers=headers, json=data.dict())

    if r.status_code != 200:
        raise HTTPException(status_code=401, detail=r.text)

    return r.json()


# ===== VERIFY TOKEN (VALIDASI KE SUPABASE) =====
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    r = requests.get(
        f"{SUPABASE_URL}/auth/v1/user",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {token}"
        }
    )

    if r.status_code != 200:
        raise HTTPException(status_code=401, detail="Token tidak valid")

    return token


# ===== GET =====
@appjwt.get("/mahasiswa")
def get_data(token=Depends(verify_token)):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {token}"
    }

    r = requests.get(BASE_URL, headers=headers)

    return safe_json(r)


# ===== INSERT =====
@appjwt.post("/mahasiswa")
def create_data(data: Mahasiswa, token=Depends(verify_token)):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    r = requests.post(BASE_URL, headers=headers, json=data.dict())

    return safe_json(r)


# ===== UPDATE =====
@appjwt.put("/mahasiswa/{id}")
def update_data(id: str, data: Mahasiswa, token=Depends(verify_token)):
    url = f"{BASE_URL}?id=eq.{id}"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    r = requests.patch(url, headers=headers, json=data.dict())

    return safe_json(r)


# ===== DELETE =====
@appjwt.delete("/mahasiswa/{id}")
def delete_data(id: str, token=Depends(verify_token)):
    url = f"{BASE_URL}?id=eq.{id}"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {token}"
    }

    r = requests.delete(url, headers=headers)

    return safe_json(r)