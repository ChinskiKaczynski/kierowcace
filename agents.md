# AGENTS.md dla projektu KierowcaCE.pl

Ten plik zawiera instrukcje dla Codex, aby wspierać rozwój projektu KierowcaCE.pl zgodnie z planem PoC v2 (16 lipca 2025). Celem jest uruchomienie minimalnego, produkcyjnego portalu ofert pracy dla kierowców C+E w ≤ 4 tygodnie przy koszcie ≤ 50 zł/m-c.

## Konwencje kodowania

### Python (FastAPI, SQLAlchemy)
- Formatowanie zgodne z PEP 8.
- Nazwy zmiennych i funkcji w `snake_case`.
- Dokumentacja w stylu docstring.
- Używaj typowania (z modułu `typing`) dla funkcji i metod.

### Frontend (Jinja2, HTMX, Tailwind)
- Szablony Jinja2 w katalogu `templates`.
- Stylizacja za pomocą klas Tailwind CSS (bez build-stepu).
- HTMX dla dynamicznych elementów, np. filtrowanie ofert bez odświeżania strony.

## Organizacja kodu

- `app/`: główny katalog aplikacji
  - `main.py`: punkt wejścia FastAPI
  - `models.py`: modele SQLAlchemy
  - `routes/`: katalog z routami FastAPI
  - `scraper/`: kod scrapera OLX
  - `templates/`: szablony Jinja2
- `data/`: dane scrapowane (np. `jobs.jsonl`)
- `tests/`: testy jednostkowe i integracyjne

## Testowanie

- Uruchamiaj testy za pomocą `pytest`.
- Pokrycie testami ≥ 80%.
- Testuj:
  - Scrapera (mockowanie odpowiedzi HTTP).
  - Routy FastAPI (`/jobs`, `/search`).
  - Deduplikację ofert (constraint `UNIQUE` na `job_hash`).

## Nawigacja po kodzie

- `app/main.py`: inicjalizacja FastAPI i konfiguracja aplikacji.
- `app/models.py`: definicje modeli bazy danych (np. tabela `jobs`).
- `app/routes/jobs.py`: routy dla ofert pracy i wyszukiwania.
- `app/scraper/olx.py`: scraper OLX zapisujący dane do `.jsonl`.
- `app/templates/index.html`: główny szablon strony z listą ofert.

## Instrukcje dla scrapera

- Uruchamianie: `python -m app.scraper.olx`.
- Dane zapisywane w `data/jobs.jsonl`.
- Używaj `requests` i `parsel` do scrapowania OLX.
- Limit: 30 requestów/min, aby uniknąć blokady.
- Logowanie duplikatów do `duplicates.log`.

## Instrukcje dla bazy danych

- Schemat w `app/models.py`:
  ```sql
  CREATE TABLE jobs (
      id INTEGER PRIMARY KEY,
      company TEXT NOT NULL,
      city TEXT,
      title TEXT,
      salary_min INT,
      salary_max INT,
      url TEXT,
      job_hash TEXT UNIQUE
  );
  ```
- Używaj SQLite z trybem WAL.
- Deduplikacja: `INSERT OR IGNORE` na podstawie `job_hash` (SHA256 z `company|city|slug(title)`).
- Migracja do Postgres planowana przy >10k UU/m-c z użyciem Alembic.

## Instrukcje dla frontend

- Szablony Jinja2 renderowane przez FastAPI.
- HTMX dla asynchronicznych requestów, np. checkbox „Pokaż tylko oferty z widełkami”.
- Badge „Widełki ✔” dla ofert z `salary_min` i `salary_max`.
- Stylizacja z Tailwind CSS (inline w HTML).

## Instrukcje dla deploymentu

- Deploy na VPS Hetzner CX11 (50 zł/m-c).
- Używaj Caddy jako serwera HTTP z auto-TLS.
- Konfiguracja w pliku `Caddyfile`.
- Cron scraper za pomocą `systemd.timer`.

## Instrukcje dla marketingu

- Monitoruj:
  - UU (Unique Users) – cel: ≥100 UU w 7 dni po Sprincie 4.
  - Subskrybentów newslettera – cel: ≥25 sub w 7 dni.
- Kampanie:
  - FB Ads: budżet 150 zł, CPM < 20 zł.
  - Cold email: 50 firm z CEIDG.
  - Posty w grupach FB „Kierowcy C+E praca”.

## Instrukcje dla ryzyka

- **Blokada scrapera OLX**:
  - Rotacja User-Agent, limit 30 req/min.
  - Fallback: ręczne oferty z formularza CSV/JSON.
  - Proxy Smartproxy (25 zł/m-c, eskalacja do 80 zł przy 100 MB).
- **Brak ruchu**:
  - Wykonaj plan Go-To-Market, rewizja po Sprincie 4.
- **Firmy nie płacą**:
  - Early-bird: 49 zł/30 dni dla 10 firm.
  - Case study z UU i CV.
- **RODO**:
  - Brak CV w bazie.
  - Jasna polityka prywatności.
  - Dane kontaktowe firm → e-mail bezpośrednio.

## Roadmap

- **Sprint 1**: Lokalna baza SQLite + scraper OLX → 100 unikalnych ofert w `.jsonl`.
- **Sprint 2**: FastAPI `/jobs`, `/search` + Jinja2 z badge widełek (TTFB < 150 ms).
- **Sprint 3**: Cron scraper, deduplikacja, formularz CSV/JSON (90% ofert live ≤ 2h).
- **Sprint 4**: Landing, sitemap, newsletter, start FB/Google Ads (≥100 UU, ≥25 sub).
