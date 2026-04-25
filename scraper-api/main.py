import logging
from fastapi import FastAPI, Query
from typing import List, Dict, Any

from scrapers import JobScraperFactory, deduplicate_jobs


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("scraper")


app = FastAPI(title="Career Ops Scraper API")


@app.get("/")
def read_root():
    return {"message": "Career Ops Scraper is running"}


@app.get("/scrape")
def run_scrape(
    term: str = Query("Machine Learning Engineer", description="Job title to search"),
    location: str = Query("Argentina", description="Location"),
    results: int = Query(20, description="Results per site"),
    days_old: int = Query(15, description="Search range in days"),
    remote: bool = Query(True, description="Filter for remote jobs")
) -> Dict[str, List[Dict[str, Any]]]:
    """Búsqueda unificada: Plataformas generales + ATS + Energía"""
    # Crear instancias concretas desde la fábrica (Strategy + Factory)
    general = JobScraperFactory.create('general')
    ats = JobScraperFactory.create('ats')
    energy = JobScraperFactory.create('energy')

    all_jobs: List[Dict[str, Any]] = []
    all_jobs.extend(general.scrape(term=term, location=location, results=results, days_old=days_old))
    all_jobs.extend(ats.scrape(term=term, location=location, days_old=days_old))
    all_jobs.extend(energy.scrape(location=location, days_old=days_old))

    final_list = deduplicate_jobs(all_jobs)
    logger.info(f"🏁 Scrape finalizado. Total único: {len(final_list)}")
    return {"results": final_list}


@app.get("/scrape/energy")
def run_energy_scrape(
    days_old: int = Query(15, description="Search range in days")
) -> Dict[str, List[Dict[str, Any]]]:
    """Búsqueda especializada para empresas energéticas argentinas"""
    energy = JobScraperFactory.create('energy')
    results = energy.scrape(location="Argentina", days_old=days_old)
    unique_results = deduplicate_jobs(results)
    logger.info(f"⚡ Búsqueda energía finalizada. Resultados únicos: {len(unique_results)}")
    return {"results": unique_results}
