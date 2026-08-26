🇬🇧 [English version](README.md)

# Aplikacja monitorująca terapię ADHD

Aplikacja desktopowa (PyQt6) + backend FastAPI do rejestrowania leków w terapii ADHD i obiektywnego mierzenia koncentracji przed i po dawce, z panelem lekarza do przeglądu wyników.

## Problem

Pacjenci z ADHD i ich lekarze mają trudność w obiektywnym ocenianiu skuteczności terapii farmakologicznej. Dostępne aplikacje albo rejestrują przyjmowane leki, albo oferują grę/trening koncentracji — rzadko oba połączone, i rzadko z mechanizmem współpracy pacjent-lekarz.

## Co robi aplikacja

- Pacjenci rejestrują przyjmowane leki (czas, dawka, nazwa)
- Krótka gra testująca koncentrację/refleks, rozgrywana przed i po zażyciu leku
- Wyniki gry i ankiety nastroju zapisywane są automatycznie
- Lekarz ma panel do przeglądu historii pacjenta, porównania wyników „przed vs po” i śledzenia postępów w czasie
- Widok kalendarza, profile pacjenta i lekarza, logowanie/rejestracja

## Architektura

- **Backend** — FastAPI (Python), MongoDB przez Motor/PyMongo, MinIO do przechowywania plików, autoryzacja JWT (python-jose, bcrypt), konteneryzacja Docker
- **Frontend** — klient desktopowy PyQt6: niestandardowa belka tytułowa i motywy, widok kalendarza, osobne panele dla pacjenta i lekarza, kod podzielony na modułowe komponenty UI

## Status

Projekt akademicki. Aplikacja działała end-to-end w fazie developmentu, ale nigdy nie została przetestowana z prawdziwymi pacjentami ani w warunkach klinicznych — traktuj ją jako działający prototyp, nie zwalidowane narzędzie medyczne. Nierozwijana aktywnie.
