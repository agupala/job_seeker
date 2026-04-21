import logging
from fastapi import FastAPI, Query
from typing import List, Optional
from jobspy import scrape_jobs
import pandas as pd
import os
import json

# Configuración de logs para ver en 'docker logs -f'
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
):
    """
    Búsqueda unificada: Plataformas generales + ZipRecruiter + Portales ATS (vía Google) + Energía.
    """
    # 1. Plataformas principales (ahora con ZipRecruiter)
    sites = ["linkedin", "indeed", "glassdoor", "google", "zip_recruiter"]
    all_jobs = []
    
    logger.info(f"🚀 Iniciando scrape general para '{term}' en {location} (últimos {days_old} días)")
    
    try:
        jobs = scrape_jobs(
            site_name=sites,
            search_term=term,
            location=location,
            results_wanted=results,
            hours_old=days_old * 24,
            country_indeed='Argentina',
        )
        if not jobs.empty:
            df = jobs[['site', 'job_url', 'title', 'company', 'location', 'date_posted', 'description']]
            records = df.fillna("").to_dict(orient="records")
            all_jobs.extend(records)
            logger.info(f"✅ Búsqueda general completada. Items encontrados: {len(records)}")
    except Exception as e:
        logger.error(f"❌ Error en scrape general: {e}")

    # 2. Búsqueda dirigida a ATS (Greenhouse/Lever) vía Google Jobs
    # Esto encuentra vacantes en portales corporativos que no siempre llegan a LinkedIn
    ats_queries = [
        f"site:greenhouse.io {term} {location}",
        f"site:lever.co {term} {location}"
    ]
    
    for query in ats_queries:
        logger.info(f"🔍 Buscando en portales ATS con query: '{query}'")
        try:
            ats_jobs = scrape_jobs(
                site_name=["google"],
                search_term=query,
                location=location,
                results_wanted=10,
                hours_old=days_old * 24,
            )
            if not ats_jobs.empty:
                df_ats = ats_jobs[['site', 'job_url', 'title', 'company', 'location', 'date_posted', 'description']]
                records = df_ats.fillna("").to_dict(orient="records")
                all_jobs.extend(records)
                logger.info(f"✨ Portales ATS para '{query}' devolvieron {len(records)} resultados")
        except Exception as e:
            logger.warning(f"⚠️ Error buscando ATS para {query}: {e}")

    # 3. Búsqueda específica en empresas de Energía (YPF, etc.)
    companies = ["YPF", "Pampa Energía", "Pan American Energy", 
        "Tecpetrol", "Shell", "Vista Energy",
        "Techint", "ExxonMobil", "Chevron", "Total Energies",
        ]
    for company in companies:
        query = f"{company} Careers {term}"
        logger.info(f"🏢 Scrapeando portal específico de: {company}")
        try:
            energy_jobs = scrape_jobs(
                site_name=["google"],
                search_term=query,
                location=location,
                results_wanted=3,
                hours_old=days_old * 24,
            )
            if not energy_jobs.empty:
                df_energy = energy_jobs[['site', 'job_url', 'title', 'company', 'location', 'date_posted', 'description']]
                records = df_energy.fillna("").to_dict(orient="records")
                all_jobs.extend(records)
        except:
            continue

    # Deduplicación por URL
    unique_jobs = {j['job_url']: j for j in all_jobs}.values()
    final_list = list(unique_jobs)
    
    logger.info(f"🏁 Scrape finalizado. Total único de vacantes encontradas: {len(final_list)}")
    
    return {"results": final_list}

@app.get("/scrape/energy")
def run_energy_scrape(
    days_old: int = Query(15, description="Search range in days")
):
    """
    Búsqueda específica para empresas energéticas argentinas
    """
    companies = ["YPF", "Pampa Energía", "Pan American Energy", "Tecpetrol", "Shell", "Vista Energy"]
    all_results = []
    
    for company in companies:
        queries = [
            f"{company} Careers Machine Learning", 
            f"{company} Data Science AI", 
            f"{company} Ingeniero de Datos"
        ]
        for query in queries:
            logger.info(f"⚡ Búsqueda especializada Energía: {query}")
            try:
                jobs = scrape_jobs(
                    site_name=["google"],
                    search_term=query,
                    location="Argentina",
                    results_wanted=5,
                    hours_old=days_old * 24,
                )
                if not jobs.empty:
                    df = jobs[['site', 'job_url', 'title', 'company', 'location', 'date_posted', 'description']]
                    all_results.extend(df.to_dict(orient="records"))
            except:
                continue
            
    unique_results = {j['job_url']: j for j in all_results}.values()
    return {"results": list(unique_results)}
