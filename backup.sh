#!/bin/bash

# Configuración
export PATH=$PATH:/usr/local/bin
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
CURRENT_BACKUP="$BACKUP_DIR/backup_$TIMESTAMP"

# Crear carpeta de backup
mkdir -p "$CURRENT_BACKUP"

echo "🚀 Iniciando backup automatizado..."

# 1. Exportar Workflows directamente desde el contenedor de n8n
echo "📦 Exportando todos los workflows..."
if docker exec job_seeker-n8n-1 n8n export:workflow --all --output=/tmp/master_workflows.json > /dev/null 2>&1; then
    docker cp job_seeker-n8n-1:/tmp/master_workflows.json "./n8n/workflow.json"
    # Dar formato al JSON para que sea legible
    jq . "./n8n/workflow.json" > "./n8n/workflow_tmp.json" && mv "./n8n/workflow_tmp.json" "./n8n/workflow.json"
    cp "./n8n/workflow.json" "$CURRENT_BACKUP/all_workflows_backup.json"
    echo "✅ Workflows exportados y formateados."
else
    echo "❌ Error: No se pudo conectar con el contenedor n8n. ¿Está encendido?"
    exit 1
fi

# Exportar cada workflow por separado para el backup (ordenado)
mkdir -p "$CURRENT_BACKUP/individual_workflows"
docker exec job_seeker-n8n-1 n8n export:workflow --all --separate --output=/tmp/sep/ > /dev/null
docker cp job_seeker-n8n-1:/tmp/sep/ "$CURRENT_BACKUP/individual_workflows/"

# 2. Dump de la Base de Datos Postgres
echo "🗄️  Haciendo dump de la base de datos..."
if docker exec job_seeker-db-1 pg_dump -U n8n_user job_seeker_db > "$CURRENT_BACKUP/database.sql" 2>/dev/null; then
    echo "✅ Base de datos respaldada."
else
    echo "❌ Error: No se pudo conectar con la base de datos."
fi

# 3. Copiar archivos de configuración importantes
echo "📄 Copiando archivos de configuración (.env, docker-compose)..."
cp .env "$CURRENT_BACKUP/.env" 2>/dev/null || echo "⚠️  No se encontró el archivo .env"
cp docker-compose.yml "$CURRENT_BACKUP/docker-compose.yml"
cp -r scraper-api "$CURRENT_BACKUP/scraper-api" 2>/dev/null # Opcional: copia el código del scraper

# 4. Crear un reporte de qué se guardó
echo "Backup completado en: $CURRENT_BACKUP" > "$CURRENT_BACKUP/info.txt"
echo "Contenido:" >> "$CURRENT_BACKUP/info.txt"
ls -R "$CURRENT_BACKUP" >> "$CURRENT_BACKUP/info.txt"

echo "✅ ¡Todo listo! El backup se guardó en: $CURRENT_BACKUP"
echo "--------------------------------------------------------"
echo "Tip: Puedes correrlo con: ./backup.sh"
