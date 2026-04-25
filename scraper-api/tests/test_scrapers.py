import sys
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRAPERS_PY = ROOT / "scrapers.py"
CONFIG_PY = ROOT / "config.py"


def load_package_modules():
    """Carga `config` y `scrapers` agregando el directorio raíz al path."""
    if str(ROOT) not in sys.path:
        sys.path.append(str(ROOT))
    
    import config as cfg
    import scrapers as scr
    
    # Recargar para asegurar que tenemos la versión más reciente si se corre en el mismo proceso
    import importlib
    importlib.reload(cfg)
    importlib.reload(scr)
    
    return scr, cfg


def make_df(row: dict):
    return pd.DataFrame([row])


def test_general_scraper_returns_results(monkeypatch):
    scr, cfg = load_package_modules()

    sample = {c: f"val_{c}" for c in cfg.COLUMNS}
    sample[cfg.COLUMNS[1]] = "http://example.com/1"

    def fake_scrape_jobs(**kwargs):
        return make_df(sample)

    monkeypatch.setattr(scr, "scrape_jobs", fake_scrape_jobs)

    gen = scr.GeneralScraper()
    results = gen.scrape(term="ML", location="Argentina", results=1, days_old=1)

    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0][cfg.COLUMNS[1]] == "http://example.com/1"


def test_ats_scraper_multiple_patterns(monkeypatch):
    scr, cfg = load_package_modules()

    sample = {c: f"val_{c}" for c in cfg.COLUMNS}
    sample[cfg.COLUMNS[1]] = "http://example.com/ats"

    def fake_scrape_jobs(**kwargs):
        return make_df(sample)

    monkeypatch.setattr(scr, "scrape_jobs", fake_scrape_jobs)

    ats = scr.ATSScraper()
    results = ats.scrape(term="ML", location="Argentina", days_old=1)

    # debe devolver al menos una entrada por cada patrón ATS
    assert isinstance(results, list)
    assert len(results) >= len(cfg.ATS_PATTERNS)


def test_deduplicate_jobs():
    scr, cfg = load_package_modules()

    j1 = {c: f"a_{c}" for c in cfg.COLUMNS}
    j1[cfg.COLUMNS[1]] = "dup_url"
    j2 = {c: f"b_{c}" for c in cfg.COLUMNS}
    j2[cfg.COLUMNS[1]] = "dup_url"

    out = scr.deduplicate_jobs([j1, j2])
    assert isinstance(out, list)
    assert len(out) == 1
    assert out[0][cfg.COLUMNS[1]] == "dup_url"
