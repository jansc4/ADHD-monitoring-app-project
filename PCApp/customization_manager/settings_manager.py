import json
from pathlib import Path

class SettingsManager:
    """
    Klasa zarządzająca ustawieniami aplikacji – font, motyw, język.
    Obsługuje wartości bieżące oraz listy możliwych wartości.
    """

    def __init__(self):
        """
        Inicjalizuje manager, wczytując plik JSON z ustawieniami.
        """
        base_dir = Path(__file__).resolve().parent.parent
        self.settings_path = base_dir / 'data' / 'settings.json'

        self.default_settings = {
            "font_family": "Segoe UI",
            "font_families": ["Arial", "Calibri", "NewTimesRoman", "Segoe UI"],
            "font_size": 14,
            "font_sizes": [12, 14, 16, 18],
            "theme": "dark",
            "themes": ["light", "dark"],
            "language": "lang_en",
            "languages": ["lang_en", "lang_pl"]
        }

        self.settings = self.load_settings()

    def load_settings(self):
        """
        Wczytuje ustawienia z pliku JSON lub tworzy domyślne.
        """
        if self.settings_path.exists():
            try:
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return {**self.default_settings, **data}
            except (json.JSONDecodeError, IOError):
                print("Błąd wczytywania settings.json – użyto ustawień domyślnych.")
        return self.default_settings.copy()

    def save_settings(self):
        """
        Zapisuje bieżące ustawienia do pliku JSON.
        """
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except IOError:
            print("Nie udało się zapisać ustawień.")

    def get(self, key):
        """
        Pobiera wartość danego klucza.
        """
        return self.settings.get(key, self.default_settings.get(key))

    def set(self, key, value):
        """
        Ustawia wartość danego klucza i zapisuje do pliku.
        """
        self.settings[key] = value
        self.save_settings()

    def get_available_values(self, key):
        """
        Pobiera listę możliwych wartości danego parametru.
        Przykład: dla 'font_family' zwróci 'font_families'.
        """
        plural_key = key + 's' if not key.endswith('s') else key + '_list'
        return self.settings.get(plural_key, self.default_settings.get(plural_key, []))

    def get_all(self):
        """
        Zwraca cały słownik ustawień.
        """
        return self.settings.copy()
