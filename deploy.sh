#!/bin/bash
set -e

# ============================================================
# Script de Despliegue - CodeAcademy Backend
# VPS: Ubuntu 24.04 LTS - DigitalOcean
# IP: 159.223.133.69
# ============================================================

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_DIR="/opt/codeacademy/CodeAcademy_bakend"
VENV_DIR="$PROJECT_DIR/venv"
REPO_URL="https://github.com/sergio001g/CodeAcademy_bakend.git"
SERVER_IP="159.223.133.69"
DB_NAME="codeacademy"
DB_USER="codeacademy"
DB_PASSWORD="C0d3Ac4d3my_Pr0d_2026"
SECRET_KEY="xK9mP2nQ7rS4tU8vW1xY3zA5bC7dE9fG2hJ4kL6mN8pR0sT"

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  DESPLIEGUE CODEACADEMY BACKEND${NC}"
echo -e "${GREEN}============================================${NC}"

# ---- 1. ACTUALIZAR SISTEMA ----
echo -e "\n${YELLOW}[1/10] Actualizando sistema...${NC}"
export DEBIAN_FRONTEND=noninteractive
apt update -y
apt upgrade -y

# ---- 2. INSTALAR DEPENDENCIAS ----
echo -e "\n${YELLOW}[2/10] Instalando dependencias del sistema...${NC}"
apt install -y python3 python3-venv python3-pip python3-dev \
    postgresql postgresql-contrib \
    nginx \
    git \
    libpq-dev \
    curl \
    ufw

# ---- 3. CONFIGURAR POSTGRESQL ----
echo -e "\n${YELLOW}[3/10] Configurando PostgreSQL...${NC}"
systemctl start postgresql
systemctl enable postgresql

sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"

sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

sudo -u postgres psql -c "ALTER ROLE $DB_USER SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE $DB_USER SET timezone TO 'America/Bogota';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

echo -e "${GREEN}   ✓ PostgreSQL configurado: DB=$DB_NAME, USER=$DB_USER${NC}"

# ---- 4. CLONAR REPOSITORIO ----
echo -e "\n${YELLOW}[4/10] Clonando repositorio...${NC}"
mkdir -p /opt/codeacademy
if [ -d "$PROJECT_DIR" ]; then
    cd "$PROJECT_DIR"
    git fetch --all
    git reset --hard origin/main
    echo -e "${GREEN}   ✓ Repositorio actualizado${NC}"
else
    cd /opt/codeacademy
    git clone "$REPO_URL"
    cd "$PROJECT_DIR"
    echo -e "${GREEN}   ✓ Repositorio clonado${NC}"
fi

# ---- 5. ENTORNO VIRTUAL Y DEPENDENCIAS ----
echo -e "\n${YELLOW}[5/10] Configurando entorno virtual Python...${NC}"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt
pip install django-cors-headers whitenoise

echo -e "${GREEN}   ✓ Dependencias instaladas${NC}"

# ---- 6. CREAR ARCHIVO .env ----
echo -e "\n${YELLOW}[6/10] Configurando variables de entorno (.env)...${NC}"
cat > "$PROJECT_DIR/.env" << ENVEOF
# ============================================================
# Variables de Entorno - Produccion
# CodeAcademy Backend
# ============================================================
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=$SERVER_IP,localhost,127.0.0.1

# Base de datos PostgreSQL
POSTGRES_DB=$DB_NAME
POSTGRES_USER=$DB_USER
POSTGRES_PASSWORD=$DB_PASSWORD
DB_HOST=localhost
DB_PORT=5432
ENVEOF

echo -e "${GREEN}   ✓ Archivo .env creado${NC}"

# ---- 7. PARCHEAR SETTINGS.PY PARA PRODUCCION ----
echo -e "\n${YELLOW}[7/10] Configurando Django para producción...${NC}"

# Agregar STATIC_ROOT si no existe
if ! grep -q "STATIC_ROOT" "$PROJECT_DIR/core/settings.py"; then
    sed -i "/^STATIC_URL/a\\
STATIC_ROOT = BASE_DIR / 'staticfiles'" "$PROJECT_DIR/core/settings.py"
fi

# Agregar MEDIA settings si no existen
if ! grep -q "MEDIA_URL" "$PROJECT_DIR/core/settings.py"; then
    cat >> "$PROJECT_DIR/core/settings.py" << 'SETTINGSEOF'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
SETTINGSEOF
fi

# Agregar CORS settings
if ! grep -q "corsheaders" "$PROJECT_DIR/core/settings.py"; then
    sed -i "s/'apps',/'corsheaders',\n    'apps',/" "$PROJECT_DIR/core/settings.py"
    sed -i "s/'django.middleware.common.CommonMiddleware',/'corsheaders.middleware.CorsMiddleware',\n    'django.middleware.common.CommonMiddleware',/" "$PROJECT_DIR/core/settings.py"
    cat >> "$PROJECT_DIR/core/settings.py" << 'CORSEOF'

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORSEOF
fi

# Crear directorio media
mkdir -p "$PROJECT_DIR/media"
mkdir -p "$PROJECT_DIR/staticfiles"

echo -e "${GREEN}   ✓ Settings.py configurado para producción${NC}"

# ---- 8. MIGRACIONES Y DATOS INICIALES ----
echo -e "\n${YELLOW}[8/10] Ejecutando migraciones y configuración inicial...${NC}"
cd "$PROJECT_DIR"
source "$VENV_DIR/bin/activate"

python manage.py migrate --noinput
python manage.py configurar_roles --email admin@codeacademy.com --password admin123
python manage.py collectstatic --noinput

echo -e "${GREEN}   ✓ Migraciones ejecutadas, roles configurados, archivos estáticos recopilados${NC}"

# ---- 9. CONFIGURAR GUNICORN (SYSTEMD) ----
echo -e "\n${YELLOW}[9/10] Configurando Gunicorn...${NC}"

# Crear socket de Gunicorn
cat > /etc/systemd/system/gunicorn.socket << 'SOCKETEOF'
[Unit]
Description=gunicorn socket para CodeAcademy

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
SOCKETEOF

# Crear servicio de Gunicorn
cat > /etc/systemd/system/gunicorn.service << SERVICEEOF
[Unit]
Description=Gunicorn daemon para CodeAcademy Backend
Requires=gunicorn.socket
After=network.target postgresql.service

[Service]
User=root
Group=www-data
WorkingDirectory=$PROJECT_DIR
ExecStart=$VENV_DIR/bin/gunicorn \\
    --access-logfile /var/log/gunicorn/access.log \\
    --error-logfile /var/log/gunicorn/error.log \\
    --workers 3 \\
    --bind unix:/run/gunicorn.sock \\
    core.wsgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Crear directorio de logs
mkdir -p /var/log/gunicorn

# Habilitar y arrancar Gunicorn
systemctl daemon-reload
systemctl start gunicorn.socket
systemctl enable gunicorn.socket
systemctl start gunicorn
systemctl enable gunicorn

echo -e "${GREEN}   ✓ Gunicorn configurado y ejecutándose${NC}"

# ---- 10. CONFIGURAR NGINX ----
echo -e "\n${YELLOW}[10/10] Configurando Nginx...${NC}"

cat > /etc/nginx/sites-available/codeacademy << NGINXEOF
server {
    listen 80;
    server_name $SERVER_IP;

    client_max_body_size 10M;

    # Archivos estáticos
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Archivos media
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 30d;
    }

    # Favicon
    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }

    # Proxy a Gunicorn
    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Host \$host;
        proxy_redirect off;
    }
}
NGINXEOF

# Habilitar sitio y deshabilitar default
ln -sf /etc/nginx/sites-available/codeacademy /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Verificar configuración de Nginx
nginx -t

# Reiniciar Nginx
systemctl restart nginx
systemctl enable nginx

echo -e "${GREEN}   ✓ Nginx configurado y ejecutándose${NC}"

# ---- FIREWALL ----
echo -e "\n${YELLOW}Configurando firewall...${NC}"
ufw allow 'Nginx Full'
ufw allow OpenSSH
echo "y" | ufw enable 2>/dev/null || true

echo -e "${GREEN}   ✓ Firewall configurado${NC}"

# ---- VERIFICACIÓN ----
echo -e "\n${GREEN}============================================${NC}"
echo -e "${GREEN}  ¡DESPLIEGUE COMPLETADO EXITOSAMENTE!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "  ${YELLOW}URLs disponibles:${NC}"
echo -e "  Home:    http://$SERVER_IP/"
echo -e "  API:     http://$SERVER_IP/api/"
echo -e "  Swagger: http://$SERVER_IP/api/docs/"
echo -e "  Redoc:   http://$SERVER_IP/api/docs/redoc/"
echo -e "  Admin:   http://$SERVER_IP/admin/"
echo ""
echo -e "  ${YELLOW}Credenciales Admin:${NC}"
echo -e "  Email:    admin@codeacademy.com"
echo -e "  Password: admin123"
echo ""
echo -e "  ${YELLOW}Estado de servicios:${NC}"
systemctl status gunicorn --no-pager -l || true
systemctl status nginx --no-pager -l || true
echo ""
echo -e "${GREEN}============================================${NC}"
