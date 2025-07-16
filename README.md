# KierowcaCE

Minimal FastAPI portal for C+E job listings with simple deduplication and salary filter.

## Setup

```bash
pip install -r requirements.txt
```

Run the application:

```bash
uvicorn app.main:app
```

Visit `http://localhost:8000` to browse jobs. Individual offers are available at
`/jobs/{id}`.

Run the scraper:

```bash
python -m app.scraper.olx
```

Scraped jobs are stored in `data/jobs.jsonl`. Ensure the `data/` directory exists:

```bash
mkdir -p data
```

Run tests with coverage:

```bash
pytest --cov=app -q
```
