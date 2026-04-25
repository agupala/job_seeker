"""
Implementación de Strategy + Factory para scrapers.

Cada scraper implementa la misma interfaz `ScraperStrategy.scrape(...)`.
La fábrica `JobScraperFactory` devuelve instancias concretas según el
tipo solicitado. Esto permite cambiar implementaciones sin tocar
el orquestador (principio Open/Closed).

Los scrapers usan `jobspy.scrape_jobs` y retornan listas de diccionarios
con las columnas estándar definidas en `config.COLUMNS`.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from jobspy import scrape_jobs
import logging

from config import GENERAL_SITES, ATS_PATTERNS, ENERGY_COMPANIES, ENERGY_JOB_TITLES, COLUMNS

logger = logging.getLogger("scraper")


class ScraperStrategy(ABC):
    """Interfaz mínima que deben implementar los scrapers."""

    @abstractmethod
    def scrape(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """Ejecuta la búsqueda y retorna lista de empleos."""
        raise NotImplementedError


def _call_jobspy(search_term: str, location: str, site_names: List[str], results_wanted: int, hours_old: int) -> List[Dict[str, Any]]:
    """Wrapper central para llamar a jobspy y normalizar resultados.

    Centralizar aquí facilita cambios futuros y manejo de errores.
    """
    try:
        df = scrape_jobs(
            site_name=site_names,
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            hours_old=hours_old,
            country_indeed='Argentina'
        )
        if df.empty:
            return []
        return df[COLUMNS].fillna("").to_dict(orient="records")
    except Exception as e:
        logger.error(f"Error en jobspy para '{search_term}': {e}")
        return []


class GeneralScraper(ScraperStrategy):
    """Scraper para plataformas principales (LinkedIn, Indeed, Glassdoor, etc.)."""

    def scrape(self, term: str, location: str, results: int, days_old: int) -> List[Dict[str, Any]]:
        logger.info(f"[GeneralScraper] Buscando '{term}' en {location} ({days_old}d)")
        return _call_jobspy(term, location, GENERAL_SITES, results, days_old * 24)


class ATSScraper(ScraperStrategy):
    """Scraper para búsquedas en portales ATS vía Google (Greenhouse/Lever)."""

    def scrape(self, term: str, location: str, days_old: int) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for pattern in ATS_PATTERNS:
            query = f"{pattern} {term} {location}"
            logger.info(f"[ATSScraper] Query: {query}")
            results.extend(_call_jobspy(query, location, ["google"], 10, days_old * 24))
        return results


class EnergyScraper(ScraperStrategy):
    """Scraper especializado en empresas del sector energético."""

    def scrape(self, location: str, days_old: int) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for company in ENERGY_COMPANIES:
            for title in ENERGY_JOB_TITLES:
                query = f"{company} {title}"
                logger.info(f"[EnergyScraper] Query: {query}")
                limit = 5 if "Careers" in title else 3
                results.extend(_call_jobspy(query, location, ["google"], limit, days_old * 24))
        return results


class JobScraperFactory:
    """Fábrica simple para crear scrapers según tipo.

    Uso:
        scraper = JobScraperFactory.create('general')
        jobs = scraper.scrape(...)
    """

    @staticmethod
    def create(scraper_type: str) -> ScraperStrategy:
        t = scraper_type.lower()
        if t == 'general':
            return GeneralScraper()
        if t == 'ats':
            return ATSScraper()
        if t == 'energy':
            return EnergyScraper()
        raise ValueError(f"Tipo de scraper desconocido: {scraper_type}")


def deduplicate_jobs(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Elimina duplicados por `job_url`. Retorna lista única."""
    unique = {j['job_url']: j for j in jobs}
    return list(unique.values())
