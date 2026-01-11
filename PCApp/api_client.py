import json
import requests


class APIClient:
    def __init__(self, base_url: str):
        self.base_url = (base_url or "http://127.0.0.1:8000").rstrip("/")
        self.token = None
        self.refresh_token = None

    # =====================
    # NISKOPZIOMOWE METODY
    # =====================

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def post(self, endpoint: str, data: dict):
        url = f"{self.base_url}{endpoint}"
        resp = requests.post(url, headers=self._headers(), json=data)
        return self._handle_response(resp)

    def get(self, endpoint: str, params: dict = None):
        url = f"{self.base_url}{endpoint}"
        resp = requests.get(url, headers=self._headers(), params=params)
        return self._handle_response(resp)

    def _handle_response(self, response):
        try:
            data = response.json()
        except json.JSONDecodeError:
            data = {"detail": response.text}

        if response.status_code >= 400:
            raise Exception(f"API error {response.status_code}: {data}")

        return data

    # =====================
    # METODY WYSOKIEGO POZIOMU
    # =====================

    def login(self, email: str, password: str):
        """
        Logowanie użytkownika – FORM DATA (OAuth2)
        POST /login
        """
        payload = {
            "username": email,   # backend wymaga username
            "password": password
        }

        print("Sending LOGIN payload:", payload)

        resp = requests.post(
            f"{self.base_url}/login",
            data=payload,  # FORM DATA
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        data = self._handle_response(resp)

        print("LOGIN RESPONSE:", data)

        self.token = data["access_token"]
        self.refresh_token = data.get("refresh_token")

        return data

    def register(self, email: str, password: str, role: str = "patient"):
        """
        Rejestracja użytkownika
        POST /register
        """
        payload = {
            "username": email,
            "email": email,
            "password": password,
            "role": role
        }

        print("REGISTER payload:", payload)

        return self.post("/register", payload)

    def get_current_user(self):
        """
        Pobiera dane aktualnie zalogowanego użytkownika
        """
        return self.get("/patient/me")
