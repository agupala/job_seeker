import sys
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRAPERS_PY = ROOT / "scrapers.py"
CONFIG_PY = ROOT / "config.py"


def load_package_modules():
    """Carga `scraper_api.config` y `scraper_api.scrapers` desde archivos.

    Usamos nombres de paquete ficticios (`scraper_api.*`) para que los
    imports relativos dentro de `scrapers.py` funcionen durante las pruebas.
    """
    # cargar config
    spec_cfg = spec_from_file_location("scraper_api.config", str(CONFIG_PY))
    cfg = module_from_spec(spec_cfg)
    sys.modules[spec_cfg.name] = cfg
    spec_cfg.loader.exec_module(cfg)

    # cargar scrapers (usa imports relativos a `scraper_api`)
    spec_scr = spec_from_file_location("scraper_api.scrapers", str(SCRAPERS_PY))
    scr = module_from_spec(spec_scr)
    sys.modules[spec_scr.name] = scr
    spec_scr.loader.exec_module(scr)

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
