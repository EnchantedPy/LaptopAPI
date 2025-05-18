import pytest
import requests
from pydantic import EmailStr
import random
import string


BASE_URL_AUTH = "http://127.0.0.1:8002"
BASE_URL_PROFILE = "http://127.0.0.1:8003"


def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


@pytest.mark.asyncio
async def test_full_auth_flow():
    # 1. Logout
    try:
        resp = requests.post(f"{BASE_URL_AUTH}/logout")
        print("Logout response:", resp.text)
    except Exception as e:
        print("Logout likely failed (as expected on first try):", e)

    # 2. Register
    username = random_string()
    password = "testpassword123"
    email = f"{username}@example.com"

    register_payload = {
        "name": username,
        "password": password,
        "email": email,
    }

    resp = requests.post(f"{BASE_URL_AUTH}/register", json=register_payload)
    assert resp.status_code == 200, f"Registration failed: {resp.text}"

    # 3. Login
    login_payload = {
        "username": username,
        "password": password,
    }

    resp = requests.post(f"{BASE_URL_AUTH}/login", json=login_payload)
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    
    token = resp.cookies.get("my_token")
    assert token, "Token not found in login response cookies"

    # 4. Get profile with token as cookie
    cookies = {"my_token": token}
    resp = requests.get(f"{BASE_URL_PROFILE}/get_profile", cookies=cookies)
    assert resp.status_code == 200, f"Profile fetch failed: {resp.text}"
    print("Profile:", resp.json())
