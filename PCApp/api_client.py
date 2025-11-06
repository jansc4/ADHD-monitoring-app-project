import json
import requests


class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.token = None
        self.refresh_token = None

    def set_token(self, token: str, refresh_token: str = None):
        """Ustawia token JWT po zalogowaniu."""
        self.token = token
        self.refresh_token = refresh_token

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
        """Obsługa błędów i automatyczne parsowanie JSON."""
        try:
            data = response.json()
        except json.JSONDecodeError:
            data = {"detail": response.text}

        if response.status_code >= 400:
            raise Exception(f"API error {response.status_code}: {data}")
        return data

    # --- Wygodne metody wysokiego poziomu ---

    def login(self, email: str, password: str):
        """Logowanie użytkownika i zapis tokenu."""
        payload = {"username": email, "password": password}
        data = self.post("/login", payload)
        token = data.get("access_token")
        refresh_token = data.get("refresh_token")
        if not token:
            raise Exception("Brak tokenu w odpowiedzi API.")
        self.set_token(token, refresh_token)
        return token

    def get_current_user(self):
        """Pobiera dane zalogowanego użytkownika."""
        return self.get("/users/me")
