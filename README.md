# 🚀 Job Seeker Ecosystem - Career Ops (Personal Edition)

Este proyecto es tu centro de comando personal para automatizar la búsqueda de empleo. Utiliza una arquitectura modular para rastrear vacantes, analizarlas con Inteligencia Artificial (Gemini) y notificarte solo cuando hay un match real con tu perfil.

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

