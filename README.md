# 🚀 Data Scientist Job Seeker Ecosystem 

Este proyecto es tu centro de comando personal para automatizar la búsqueda de empleo orientado a data scientists. Utiliza una arquitectura modular para rastrear vacantes, analizarlas con Inteligencia Artificial (Gemini) y notificarte solo cuando hay un match real con tu perfil.

---

## 🛠️ Tecnologías Utilizadas

- **[n8n](https://n8n.io/)**: Orquestador de flujo de trabajo (Low-code/No-code).
- **[FastAPI](https://fastapi.tiangolo.com/)**: API en Python para el scraping de vacantes.
- **[PostgreSQL](https://www.postgresql.org/)**: Base de datos para persistencia y deduplicación.
- **[Google Gemini AI](https://deepmind.google/technologies/gemini/)**: Filtro inteligente basado en LLM para evaluar afinidad técnica.
- **[Docker](https://www.docker.com/)**: Contenerización de todo el ecosistema.

---

## 📂 Estructura del Proyecto

- **`/scraper-api`**: Servicio Python que utiliza `JobSpy` para extraer ofertas de LinkedIn, Indeed y Google Jobs.
- **`/n8n`**: Directorio con la configuración de flujos (`workflow.json`).
- **`/postgres`**: Scripts de inicialización de la base de datos.
- **`/backups`**: Almacenamiento local de instantáneas del sistema.
- **`backup.sh`**: Script automatizado para respaldar workflows y base de datos.

---

## 🏃 Inicio Rápido

1. **Configurar Variables de Entorno**:
   Copia el archivo de ejemplo y completa tus credenciales (especialmente `GEMINI_API_KEY`):

   ```bash
   cp .env.example .env
   ```

2. **Levantar el Ecosistema**:

   ```bash
   docker-compose up -d --build
   ```

3. **Acceso a Servicios**:
   - **n8n**: [http://localhost:5679](http://localhost:5679) (Importa `n8n/workflow.json` al iniciar).
   - **Scraper API**: [http://localhost:8000/docs](http://localhost:8000/docs).
   - **Base de Datos**: Puerto `5434` (mapeado desde el 5432 interno).

---

## 🗄️ Gestión de la Base de Datos

Puedes ejecutar estos comandos directamente desde tu terminal para interactuar con los datos:

### Ver mejores matches (Score >= 5)

```bash
docker exec -it job_seeker-db-1 psql -U n8n_user -d job_seeker_db -c "SELECT title, company, ai_score FROM jobs WHERE ai_score >= 5 ORDER BY ai_score DESC;"
```

### Estadísticas rápidas

```bash
docker exec -it job_seeker-db-1 psql -U n8n_user -d job_seeker_db -c "SELECT processed, COUNT(*) FROM jobs GROUP BY processed;"
```

### Limpiar la base de datos (Reset total)

```bash
docker exec -it job_seeker-db-1 psql -U n8n_user -d job_seeker_db -c "TRUNCATE TABLE jobs RESTART IDENTITY;"
```

---

## 💾 Backups y Seguridad

El proyecto incluye un script robusto para no perder tus avances.

### Realizar un backup manual

```bash
./backup.sh
```

Esto creará una carpeta en `/backups` con:

- El dump completo de la DB (`database.sql`).
- Tus workflows de n8n exportados (individuales y maestros).
- Una copia de tu `.env` y configuración de Docker.

> [!TIP]
> Puedes programar un CRON en tu sistema para ejecutar `./backup.sh` diariamente.

---

## 💡 Notas de Implementación

- **Deduplicación**: El sistema utiliza la URL de la vacante como clave única para evitar procesar la misma oferta dos veces.
- **Filtro de IA**: El prompt de Gemini está diseñado para ser estricto (priorizando Ssr, Dagster y evitando perfiles Senior/Lead).
- **Puertos**: Se utiliza el puerto `5679` para n8n y `5434` para Postgres para evitar conflictos con instalaciones estándar.

---
¡Mucha suerte con el despliegue! Si tenés dudas, consultame. 🦾

## 🧭 Patrones de diseño usados (POO simple)

Para mantener el código claro y abierto a cambios, la implementación del servicio de
scraping (`/scraper-api`) usa una combinación de **Strategy** + **Factory**.

- Strategy: cada tipo de scraping (general, ATS, energía) implementa la misma interfaz
   (`scrape(...)`). Esto permite intercambiar implementaciones sin cambiar el orquestador.
- Factory: una fábrica simple (`JobScraperFactory`) crea instancias concretas según
   el tipo (`'general'`, `'ats'`, `'energy'`).

Diagrama (Mermaid):

```mermaid
flowchart TD
   A[JobScraperFactory] -->|create general| B[General Scraper]
   A -->|create ats| C[ATS Scraper]
   A -->|create energy| D[Energy Scraper]
   subgraph Orquestador
      O[Scrape Endpoint] --> B
      O --> C
      O --> D
      O --> E[deduplicate_jobs()]
   end
```

Ventajas rápidas:

- Single Responsibility: cada scraper hace una cosa.
- Open/Closed: agregás un nuevo scraper y la fábrica lo expone sin tocar el orquestador.
- Fácil de testear: cada estrategia se puede mockear/ejecutar aislada.

Si más adelante querés validación de inputs y documentación, se puede agregar `Pydantic`
con modelos `ScrapeRequest` y `ScrapeResponse`.

## 🧪 Tests unitarios (breve)

Hay tests mínimos bajo `scraper-api/tests/` que verifican las piezas críticas:

- `test_general_scraper_returns_results`: mockea `jobspy.scrape_jobs` y valida que
   `GeneralScraper.scrape()` normalice el DataFrame a una lista de diccionarios.
- `test_ats_scraper_multiple_patterns`: asegura que `ATSScraper` itera sobre los
   patrones ATS y devuelve resultados por cada patrón.
- `test_deduplicate_jobs`: comprueba que la función de deduplicación elimina entradas
   con la misma `job_url`.

Cómo ejecutar (recomendado local con virtualenv):

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r scraper-api/requirements.txt
python -m pip install pytest
pytest -q
```

O dentro del contenedor (recomendado para reproducibilidad):

```bash
docker-compose exec scraper pytest -q
# o si preferís un contenedor efímero
docker-compose run --rm scraper pytest -q
```

Los tests son intencionalmente ligeros y usan `monkeypatch` para evitar llamadas reales
de red; están pensados como base para ampliar la cobertura más adelante.

