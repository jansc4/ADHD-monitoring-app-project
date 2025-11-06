# Refaktoryzacja MainWindow - Dokumentacja

## Przegląd zmian

Przeprowadzono refaktoryzację kodu głównego okna aplikacji, dzieląc monolityczny plik `main_window.py` na mniejsze, łatwiejsze w zarządzaniu komponenty.

## Nowa struktura projektu

```
PCApp/
├── ui/
│   ├── components/
│   │   ├── __init__.py
│   │   ├── title_bar.py              # Niestandardowa belka tytułowa
│   │   └── window_resize_handler.py  # Obsługa zmiany rozmiaru okna
│   ├── main_window.py                 # Główne okno aplikacji (zrefaktoryzowane)
│   ├── login_window.py                # Strona logowania
│   └── settings_dialog.py             # Floating dialog ustawień
├── main.py                            # Punkt wejścia z przekazaniem api_client
└── api_client.py                      # Klient API (zaktualizowany)
```

## Komponenty

### 1. `ui/components/title_bar.py`

**Odpowiedzialność:**
- Wyświetlanie niestandardowej belki tytułowej
- Przycisk ustawień po lewej stronie
- Przyciski sterowania oknem (min, max, fullscreen, close) po prawej

**Sygnały:**
- `close_clicked` - Zamknięcie aplikacji
- `minimize_clicked` - Minimalizacja okna
- `maximize_clicked` - Maksymalizacja/przywrócenie
- `fullscreen_clicked` - Pełny ekran
- `settings_clicked` - Otwarcie ustawień

**Użycie:**
```python
title_bar = TitleBar(theme_manager, strings_manager, parent)
title_bar.settings_clicked.connect(self.show_settings)
```

### 2. `ui/components/window_resize_handler.py`

**Odpowiedzialność:**
- Obsługa zmiany rozmiaru okna bez ramki
- Wykrywanie krawędzi/rogów do resize
- Obsługa przeciągania okna

**Użycie:**
```python
self.resize_handler = WindowResizeHandler(self)

def mousePressEvent(self, event):
    self.resize_handler.mouse_press(event)

def mouseMoveEvent(self, event):
    self.resize_handler.mouse_move(event)

def mouseReleaseEvent(self, event):
    self.resize_handler.mouse_release(event)
```

### 3. `ui/settings_dialog.py`

**Odpowiedzialność:**
- Małe, niezależne okno ustawień (floating)
- Wybór języka i motywu
- Zapisywanie ustawień

**Sygnały:**
- `settings_changed` - Emitowany po zapisaniu zmian

**Cechy:**
- Pozostaje na wierzchu (`WindowStaysOnTopHint`)
- Nie blokuje głównego okna (`Modal=False`)
- Bezramkowe (`FramelessWindowHint`)

**Użycie:**
```python
settings_dialog = SettingsDialog(settings, strings, theme, parent)
settings_dialog.settings_changed.connect(self.rerender_theme)
settings_dialog.show()
```

### 4. `ui/login_window.py`

**Odpowiedzialność:**
- Formularz logowania (email + hasło)
- Komunikacja z API
- Walidacja danych wejściowych
- Obsługa błędów

**Sygnały:**
- `login_successful(dict)` - Emitowany po udanym logowaniu z danymi użytkownika

**Cechy:**
- Animacja ładowania podczas logowania
- Wyświetlanie komunikatów błędów
- Obsługa Enter do logowania

**Użycie:**
```python
login_page = LoginPage(strings_manager, api_client, parent)
login_page.login_successful.connect(self._handle_login_success)
```

### 5. `ui/main_window.py` (zrefaktoryzowane)

**Główne zmiany:**
- Usunięto ~200 linii kodu przez ekstrakcję komponentów
- Dodano parametr `api_client` w konstruktorze
- Uproszczono obsługę zdarzeń myszy (delegacja do `WindowResizeHandler`)
- Usunięto `QStackedWidget` - teraz tylko strona logowania
- Dodano `show_settings()` do wyświetlania floating dialog

**Kluczowe metody:**
- `__init__(api_client)` - Inicjalizacja z globalnym api_client
- `show_settings()` - Wyświetla dialog ustawień
- `_handle_login_success(user_data)` - Callback po udanym logowaniu
- `rerender_theme()` - Odświeża motyw w całej aplikacji

### 6. `main.py`

**Zmiany:**
- Utworzenie globalnego `api_client`
- Przekazanie `api_client` do `MainWindow`

```python
api_client = APIClient(base_url="http://localhost:8000")
window = MainWindow(api_client)
```

### 7. `api_client.py`

**Zmiany:**
- `set_token()` przyjmuje opcjonalny `refresh_token`
- `login()` zwraca token i zapisuje refresh_token

## Przepływ danych

```
main.py
  └─> APIClient
       └─> MainWindow(api_client)
            ├─> TitleBar
            │    └─> [settings_clicked] ─> show_settings()
            │                                   └─> SettingsDialog
            │                                        └─> [settings_changed] ─> rerender_theme()
            └─> LoginPage(api_client)
                 └─> [login_successful] ─> _handle_login_success(user_data)
                                              └─> TODO: Przejście do dashboard
```

## Korzyści refaktoryzacji

### 1. **Separacja odpowiedzialności (SRP)**
- Każdy komponent ma jedną, jasno określoną odpowiedzialność
- Łatwiejsze testowanie jednostkowe

### 2. **Reużywalność**
- `TitleBar` może być użyty w innych oknach
- `WindowResizeHandler` może obsługiwać dowolne okno

### 3. **Czytelność**
- Główne okno: ~300 linii → ~250 linii
- Kod bardziej zorganizowany i zrozumiały

### 4. **Łatwość rozbudowy**
- Dodanie nowych stron/widoków jest prostsze
- Łatwo dodać nowe opcje do ustawień

### 5. **Komunikacja przez sygnały**
- Luźne powiązanie między komponentami
- Łatwa integracja z istniejącym kodem

## Dalsze kroki (TODO)

1. **Dashboard po zalogowaniu**
   - Utworzyć nowy widok po udanym logowaniu
   - Przełączyć widok w `_handle_login_success()`

2. **Zarządzanie stanem użytkownika**
   - Dodać klasę `UserSession` do przechowywania danych
   - Przekazywać `user_data` do dashboardu

3. **Konfiguracja API URL**
   - Przenieść URL API do `settings.json`
   - Lub utworzyć osobny plik `config.json`

4. **Obsługa tokenów**
   - Zapisywanie tokenów w bezpieczny sposób
   - Auto-refresh tokenów
   - Obsługa wylogowania

5. **Stylizacja**
   - Dodać style dla `SettingsDialog` w `stylesheet.css`
   - Ujednolicić wygląd wszystkich komponentów

6. **Testy**
   - Testy jednostkowe dla komponentów
   - Testy integracyjne dla przepływu logowania

## Przykłady użycia

### Dodanie nowego widoku po zalogowaniu

```python
# W main_window.py

def _handle_login_success(self, user_data: dict):
    """Obsługuje udane logowanie."""
    # Utwórz dashboard
    from ui.dashboard import DashboardPage
    self.dashboard = DashboardPage(user_data, self.api_client, self)
    
    # Zastąp widok logowania dashboardem
    layout = self.centralWidget().layout()
    layout.removeWidget(self.login_page)
    self.login_page.hide()
    layout.addWidget(self.dashboard)
```

### Dostęp do api_client z innych komponentów

```python
# Przekaż api_client jako parametr
dashboard = DashboardPage(user_data, api_client, parent)

# Lub dostęp przez rodzica
class SomeWidget(QWidget):
    def some_method(self):
        api_client = self.parent().api_client
        data = api_client.get("/some-endpoint")
```

## Migracja z starego kodu

Jeśli masz istniejący kod używający starego `MainWindow`:

1. **Dodaj api_client do konstruktora:**
   ```python
   # Stary
   window = MainWindow()
   
   # Nowy
   api_client = APIClient("http://localhost:8000")
   window = MainWindow(api_client)
   ```

2. **Zaktualizuj referencje do title_bar:**
   - Teraz `title_bar` jest instancją `TitleBar`, nie zwykłym `QWidget`
   - Używaj sygnałów zamiast bezpośredniego dostępu do przycisków

3. **Usuń referencje do nieużywanych stron:**
   - `page_show`, `page_settings` itp. - teraz są osobnymi komponentami

## Pytania i odpowiedzi

**Q: Gdzie przechowywać dane użytkownika po zalogowaniu?**
A: Rekomendowane jest utworzenie klasy `UserSession` lub przechowywanie w `MainWindow` jako atrybut.

**Q: Jak dodać więcej opcji do ustawień?**
A: Edytuj `ui/settings_dialog.py` i dodaj nowe sekcje w `_setup_ui()`.

**Q: Czy mogę używać starego main_window.py?**
A: Tak, ale zalecane jest użycie nowej wersji dla lepszej organizacji kodu.

**Q: Jak dodać animacje do okna ustawień?**
A: Użyj `QPropertyAnimation` w metodzie `show_settings()` w `main_window.py`.

## Kontakt

W razie pytań lub problemów, sprawdź dokumentację PyQt6 lub skontaktuj się z zespołem deweloperskim.
