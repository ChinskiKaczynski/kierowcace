import importlib

"""Unit tests for the OLX scraper."""

def test_parse_jobs() -> None:
    olx = importlib.import_module("app.scraper.olx")
    html = """
    <div class='css-1sw7q4x'>
        <a href='http://x.com'>Kierowca</a>
        <span class='css-19yf5ek'>Firma</span>
        <span class='css-1p8f3b8'>Warszawa</span>
        <span class='css-1q2w7lz'>100-200 zł</span>
    </div>
    """
    jobs = olx.parse_jobs(html)
    assert len(jobs) == 1
    assert jobs[0]["salary_min"] == 100
    assert jobs[0]["salary_max"] == 200
