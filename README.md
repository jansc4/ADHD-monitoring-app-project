# Aplikacja monitorująca ADHD

1\. Część biznesowa
===================

Problem
-------

Pacjenci z ADHD i ich lekarze mają trudność w obiektywnym ocenianiu skuteczności terapii farmakologicznej. Dostępne aplikacje albo rejestrują przyjmowane leki, albo oferują gry/treningi koncentracji — rzadko oba połączone i z mechanizmem współpracy pacjent-lekarz.

Customer segments (kto korzysta)
--------------------------------

*   Pacjenci z rozpoznanym ADHD (dorośli i opiekunowie młodszych pacjentów)
*   Lekarze psychiatrzy, neurolodzy i lekarze rodzinni prowadzący terapię ADHD
*   Kliniki i ośrodki zdrowia zainteresowane monitoringiem terapii
*   Badacze / studenci zainteresowani danymi do badań (możliwość anonimizacji)

Rozwiązanie (solution)
----------------------

Desktopowa aplikacja (PyQt6) łącząca:

*   rejestrację przyjmowanych leków (czas, dawka, nazwa),
*   krótką grę testującą koncentrację (przed i po leku),
*   automatyczne zapisywanie wyników testów i ankiet nastroju,
*   panel lekarza do przeglądu pacjentów, wyników i eksportu raportów.

Unique Value Proposition (UVP)
------------------------------

*   Kompleks: jedno narzędzie dla pacjenta i lekarza (połączenie dziennika leków + obiektywnego testu koncentracji).
*   Porównanie wyników „przed vs po” dla tej samej osoby i leku (czas działania, skuteczność).
*   Prosty desktopowy workflow (brak zależności od chmur; prywatność danych lokalna/serwerowa).
*   Gotowe wizualizacje (wykresy liniowe/słupkowe) ułatwiające decyzje terapeutyczne.

Model biznesowy / pomysły na rozwój
-----------------------------------

*   Darmowa wersja podstawowa (student/zaliczenie): lokalne DB SQLite.
*   Premium / kliniczna: wysyłanie wyników do centralnego serwera MongoDB, zaawansowana analiza, eksport PDF/CSV.
*   Integracje (eksport/import do EHR, API dla badań).
*   Anonimizowane dane do badań (opcjonalnie, po zgodzie).

* * *

2\. Część implementacyjna — ogólny zarys
========================================

Technologie:

*   Backend: **FastAPI** (Python) + **Docker**
*   Baza: **MongoDB** (jako docelowy) lub **SQLite** (dla prostoty i trybu lokalnego/zaliczeniowego)
*   Frontend: **PyQt6** (desktop) + **matplotlib** do wykresów

Podział: backend (API + auth + DB) i frontend (PyQt6 klient + gra + UI lekarza).

* * *

3\. Backend — projekt techniczny
================================

### Wybór bazy

*   **MongoDB** (zalecane, jeśli chcesz elastyczność schematu, łatwe dokumenty JSON, skalowanie w przyszłości).
*   **SQLite** (prostsze do uruchomienia lokalnie — dobry wybór na wersję zaliczeniową; można trzymać projekt w trybie single-file).  
    **Wskazówka:** zaprojektuj warstwę repozytorium tak, by łatwo przełączyć DB (repository pattern).

### Bezpieczeństwo

*   Hasła: hash (bcrypt / argon2).
*   Autoryzacja: **JWT** (access token krótki, refresh token dłuższy) + role (patient/doctor/admin).
*   Role check na każdym endpointzie w FastAPI (Depends).
*   HTTPS (w produkcji, np. reverse proxy nginx + certbot).
*   Ograniczenie dostępu: pacjent może widzieć tylko swoje dane; lekarz widzi tylko przypisanych pacjentów.

  ### Alternatywna struktura SQL (SQLite) — skrócona

Tabele: `users`, `medication_entries`, `test_sessions`, `test_results`, `surveys`. Zależności FK: `test_sessions.user_id -> users.id`, `medication_entries.user_id -> users.id`. Wersja SQL nadaje się gdy chcesz prostą instalację „wszystko w jednym pliku”.

* * *
4\. Frontend — PyQt6 (projekt aplikacji)
========================================

Główne komponenty UI
--------------------

*   Ekran logowania / rejestracji
*   Dashbord pacjenta
    *   Formularz dodawania wpisu leku
    *   Przycisk: „Zagraj — przed lekiem” / „Zagraj — po leku”
    *   Historia testów + wykresy (matplotlib embedded)
    *   Ankieta nastroju po każdym teście
*   Ekran lekarza
    *   Lista pacjentów
    *   Widok pacjenta: lista leków, wykresy porównawcze, surowe wyniki
    *   Możliwość eksportu CSV/PDF
*   Ustawienia aplikacji (API URL, tokeny, tryb offline/local)
