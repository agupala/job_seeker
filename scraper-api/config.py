"""
Configuración centralizada para scraper-api.

Este archivo contiene constantes que pueden modificarse sin tocar
la lógica de scraping. Mantener valores simples aquí facilita pruebas
y despliegues (por ejemplo, inyectar diferentes valores en CI/CD).

No usar Pydantic aquí para mantenerlo simple; si más adelante se
quiere validar/serializar, podemos migrar a un `Settings` con Pydantic.
"""
from typing import List

# Plataformas principales a consultar con jobspy
GENERAL_SITES: List[str] = ["linkedin", "indeed", "glassdoor", "google", "zip_recruiter"]

# Patrones para búsquedas ATS (se usan en Google Jobs queries)
ATS_PATTERNS: List[str] = ["site:greenhouse.io", "site:lever.co"]

# Empresas del sector energético argentino que queremos revisar
ENERGY_COMPANIES: List[str] = [
    "YPF", "Pampa Energía", "Pan American Energy", "Tecpetrol",
    "Shell", "Techint", "ExxonMobil", "Chevron", "Total Energies"
]

# Variantes de títulos/queries para búsquedas en empresas de energía
ENERGY_JOB_TITLES: List[str] = [
    "Careers Machine Learning", "Data Science AI", "Ingeniero de Datos",
    "Machine Learning Engineer", "Data Scientist", "AI Engineer", "MLOps"
]

# Columnas esperadas en los DataFrames devueltos por jobspy
COLUMNS: List[str] = ['site', 'job_url', 'title', 'company', 'location', 'date_posted', 'description']