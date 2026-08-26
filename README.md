🇵🇱 [Polska wersja](README.pl.md)

# ADHD Therapy Monitoring App

A desktop app (PyQt6) + FastAPI backend for tracking ADHD medication and objectively measuring concentration before and after a dose, with a doctor-facing dashboard to review results.

## Problem

Patients with ADHD and their doctors have a hard time objectively judging how well a pharmacological therapy is working. Existing apps either log medication, or offer a concentration game/training — rarely both, and rarely with a built-in patient-doctor feedback loop.

## What it does

- Patients log medication (time, dose, name)
- A short concentration/reaction game is played before and after taking medication
- Game results and mood surveys are recorded automatically
- Doctors get a dashboard to review a patient's history, compare "before vs. after" results, and track progress over time
- Calendar view, patient and doctor profiles, login/registration flow

## Architecture

- **Backend** — FastAPI (Python), MongoDB via Motor/PyMongo, MinIO for file storage, JWT-based auth (python-jose, bcrypt), containerized with Docker
- **Frontend** — PyQt6 desktop client: custom title bar and theming, calendar view, separate dashboards for patient and doctor roles, refactored into modular UI components

## Status

Built as an academic project. The app worked end-to-end in development, but it was never tested with real patients or in a clinical setting — treat it as a working prototype, not a validated medical tool. Not actively maintained.
