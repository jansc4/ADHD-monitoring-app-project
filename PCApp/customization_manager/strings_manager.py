import json
from pathlib import Path

class StringsManager:
    """
    Klasa zarządzająca stringami interfejsu aplikacji na podstawie języka.
    """

    def __init__(self, language="lang_en"):
        """
        Inicjalizuje manager, wczytując plik JSON z odpowiedniego języka.
        """
        self.lang = language.upper()
        self.strings = self.load_language()

    def load_language(self):
        """
        Wczytuje plik JSON z tekstami w danym języku.
        """

        base_dir = Path(__file__).resolve().parent.parent
        self.lang_path = base_dir / 'strings' / f'{self.lang}.json'

        if self.lang_path.exists():
            try:
                with open(self.lang_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Błąd wczytywania pliku językowego {self.lang_path.name}: {e}")
        else:
            print(f"Nie znaleziono pliku językowego: {self.lang_path}")
        return {}

    def get(self, key):
        """
        Pobiera string dla danego klucza.
        """
        return self.strings.get(key, f"[{key}]")

    def all(self):
        """
        Zwraca wszystkie stringi jako słownik.
        """
        return self.strings
