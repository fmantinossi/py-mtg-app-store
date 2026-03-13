# MTG App Store (Proof of Concept)

A Django 6 proof-of-concept that emulates an online store for Magic: The Gathering cards. It lists cards imported from the Scryfall API, lets authenticated users curate the catalog, and demonstrates how the project could evolve into a full commerce experience (search, detailed pages, CRUD, image upload, and price conversion).

## Architecture Highlights

- **Project layout** – `app/` hosts global settings, URLs, and templates; the domain logic lives in the `store/` app, while `accounts/` wraps the auth views for registration/login flows.
- **Domain model** – normalized tables for sets, colors, types, rarities, card images, and `Card` records with UUID tracking (`store/models.py`). This mirrors typical MTG data relationships and simplifies querying/filtering.
- **Views & UI** – class-based views provide pagination, search, CRUD, and detail pages; templates + static assets in `store/static` render a storefront-like layout with price conversion to BRL.
- **Data ingestion** – custom management commands (`store/management/commands`) call the public Scryfall API, transform the payload, and persist images/media locally.
- **Persistence** – PostgreSQL is the default DB (see `app/settings.py`), provisioned through Docker Compose (`infra/postgres`). Local media, logs, and SQLite are kept out-of-band so you can quickly prototype without infrastructure.
- **Observability** – a rotating log setup (`logs/requests.log`, `logs/errors.log`, `logs/business.log`) captures server events, HTTP errors, and domain actions for debugging during the POC stage.

## Tech Stack

- Python 3.12+
- Django 6.0
- PostgreSQL 16 (Dockerized)
- Pillow for image uploads
- Requests + python-dateutil for Scryfall ingestion
- docker / docker-compose for local infrastructure

## Getting Started

### 1. Clone & install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment variables

Create an `.env` file in the project root (same folder as `manage.py`). The defaults match the Docker Compose profile:

```env
DB_NAME=mtg_db
DB_USER=mtg_user
DB_PASSWORD=mtg_pass
DB_HOST=127.0.0.1
DB_PORT=5432
SECRET_KEY=change-me
DEBUG=True
```

### 3. Start PostgreSQL via Docker Compose

All infra files live under `infra/postgres/` so the Django codebase stays clean:

```bash
cd infra/postgres
docker compose up -d --build
```

- Uses the official `postgres:16-alpine` image with an optional `initdb` hook that creates the `app` schema and enables the `uuid-ossp` extension.
- Exposes port `5432` and persists data via the `pg_data` Docker volume.
- Health checks block until PostgreSQL is ready before Django connects.

### 4. Run Django

```bash
cd /path/to/py-mtg-app-store
python manage.py migrate
python manage.py createsuperuser  # optional, for /admin
python manage.py runserver 0.0.0.0:8000
```

Visit `http://localhost:8000/cards/` to browse the catalog. Anonymous users can search and inspect cards; authenticated users see Create/Update/Delete links surfaced in the UI.

## Features

- **Catalog browsing** – `/cards/` exposes a paginated grid with search and BRL price conversion (currently hard-coded for dev parity).
- **Card detail page** – richer context (set info, rarity, Oracle text, P/T, mana cost) plus secure actions for logged-in editors.
- **CRUD authoring** – `NewCardView`, `UpdateCardView`, `DeleteCardView` rely on `CardModelForm`, custom validations, and dynamic media uploads (images stored under `media/card_images/`).
- **User onboarding** – simple registration & login views built on Django’s auth forms; permissions gate write operations via `login_required`.
- **Structured logging** – rotating log files distinguish HTTP traffic, server errors, and business events.

## Data Import & Seeding

Two management commands are included for ingesting real MTG data:

| Command | Description |
| --- | --- |
| `python manage.py import_scryfall_ice` | Imports the Ice Age block. Handles pagination, normalizes type/subtype/color data, downloads images, and stores USD prices. |
| `python manage.py populate_mtg_data` | Imports several 1994-era sets (Antiquities, Revised Edition, Legends, The Dark, Fallen Empires) with similar normalization logic. |

Both commands:

1. Call Scryfall’s public REST endpoints.
2. Upsert `Set`, `Card`, and lookup tables to avoid duplicates.
3. Download card art and store it via `CardImage` (using Pillow + Django’s storage layer).
4. Provide CLI feedback to monitor ingestion progress.

> Tip: run the commands **after** `migrate` and **before** loading the UI so the catalog has real data.

## Directory Overview

```
app/            # project settings, URLs, global templates
store/          # domain logic: models, views, forms, static assets, management commands
accounts/       # lightweight registration/login views & templates
media/          # user-uploaded card art (auto-created)
logs/           # rotating log files configured in settings
infra/postgres/ # Dockerfile + compose stack for PostgreSQL 16 + init scripts
requirements.txt
manage.py
```

## Development Notes & Next Steps

- Current settings assume `DEBUG=True` and expose the secret key; harden before deploying to production.
- Tests are not yet defined (`store/tests.py`, `accounts/tests.py` are placeholders). Consider adding unit/integration coverage around the management commands and card CRUD flows.
- Static/media hosting, authentication hardening, and payment/cart logic are intentionally out-of-scope for this POC but are natural next evolutions once the catalog stabilizes.

## Troubleshooting

- **Database connection errors** – ensure Docker is running, the Postgres container is healthy (`docker compose ps`), and the `.env` matches the credentials defined in `infra/postgres/docker-compose.yml`.
- **Missing images** – the management commands create placeholder `CardImage` entries when Scryfall lacks artwork; check the `media/` folder or rerun the command if downloads fail.
- **Logging** – see `logs/errors.log` for stack traces and `logs/requests.log` for request history when debugging unexpected behavior.
