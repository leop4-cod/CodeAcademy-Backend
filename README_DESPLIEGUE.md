# Despliegue - CodeAcademy Backend API

## Informacion General del Proyecto

**CodeAcademy Backend** es una API REST construida con Django REST Framework para una plataforma de cursos en linea. Incluye autenticacion JWT, documentacion interactiva con Swagger/ReDoc, y gestion completa de cursos, usuarios, quizzes, foros y mas.

---

## URL Publica

> **Dominio:** `codeacademy-api.uaeftt-ute.site`
> **IP del servidor:** `159.223.133.69`

### URLs Disponibles

| Recurso | URL | Descripcion |
|---------|-----|-------------|
| **Home** | [https://codeacademy-api.uaeftt-ute.site/](https://codeacademy-api.uaeftt-ute.site/) | Pagina principal de bienvenida de la API |
| **API Root** | [https://codeacademy-api.uaeftt-ute.site/api/](https://codeacademy-api.uaeftt-ute.site/api/) | Raiz de la API REST, lista todos los endpoints disponibles |
| **Swagger UI** | [https://codeacademy-api.uaeftt-ute.site/api/docs/](https://codeacademy-api.uaeftt-ute.site/api/docs/) | Documentacion interactiva de la API. Permite probar endpoints directamente desde el navegador |
| **ReDoc** | [https://codeacademy-api.uaeftt-ute.site/api/docs/redoc/](https://codeacademy-api.uaeftt-ute.site/api/docs/redoc/) | Documentacion alternativa de la API con formato de referencia tecnica |
| **Admin Django** | [https://codeacademy-api.uaeftt-ute.site/admin/](https://codeacademy-api.uaeftt-ute.site/admin/) | Panel de administracion de Django para gestionar datos directamente |

---

## Credenciales de Acceso

### Superusuario (Profesor)

| Campo | Valor |
|-------|-------|
| **Usuario** | `admin` |
| **Contrasena** | `Admin1234!` |
| **Rol** | Superusuario / Administrador |

### Superusuario (Desarrollo)

| Campo | Valor |
|-------|-------|
| **Email** | `admin@codeacademy.com` |
| **Contrasena** | `admin123` |
| **Rol** | Superusuario / Administrador |

> **Nota:** Para iniciar sesion en la API via JWT, usar el endpoint `/api/auth/login/` con el campo `email` y `password`.
> Para acceder al panel Admin de Django (`/admin/`), usar las mismas credenciales.

---

## Informacion del Servidor VPS

| Parametro | Valor |
|-----------|-------|
| **Proveedor** | DigitalOcean |
| **Droplet** | ubuntu-s-1vcpu-2gb-nyc1 |
| **Sistema Operativo** | Ubuntu 24.04 LTS x64 |
| **IP Publica** | `159.223.133.69` |
| **IP Privada** | `10.116.0.4` |
| **Dominio** | `codeacademy-api.uaeftt-ute.site` |
| **Recursos** | 1 vCPU, 2GB RAM, 50GB SSD |
| **Region** | NYC1 (New York) |
| **Costo** | $12.00 / mes |

---

## 1. Configuracion del VPS

### 1.1 Creacion del Droplet

Se creo un Droplet en DigitalOcean con las siguientes especificaciones:

- **Plan**: Basic - Regular (1 vCPU, 2GB RAM, 50GB SSD)
- **Region**: NYC1 (New York City)
- **Imagen**: Ubuntu 24.04 (LTS) x64
- **Autenticacion**: Contrasena root

### 1.2 Acceso al Servidor

```bash
ssh root@159.223.133.69
# o mediante el dominio:
ssh root@codeacademy-api.uaeftt-ute.site
```

### 1.3 Actualizacion del Sistema

```bash
sudo apt update -y
sudo apt upgrade -y
```

### 1.4 Instalacion de Dependencias del Sistema

```bash
sudo apt install -y python3 python3-venv python3-pip python3-dev \
    postgresql postgresql-contrib \
    nginx \
    git \
    libpq-dev \
    curl \
    ufw \
    certbot python3-certbot-nginx
```

**Paquetes instalados:**

| Paquete | Version | Funcion |
|---------|---------|---------|
| Python 3.12 | 3.12.x | Lenguaje de programacion |
| PostgreSQL | 16.x | Base de datos relacional |
| Nginx | 1.24.x | Servidor web / reverse proxy |
| Git | Latest | Control de versiones |
| Certbot | 2.9.x | Certificados SSL (Let's Encrypt) |
| UFW | Latest | Firewall |

### 1.5 Configuracion del Firewall (UFW)

```bash
# Permitir trafico HTTP, HTTPS y SSH
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable

# Verificar estado
sudo ufw status
```

Resultado:
```
Status: active

To                         Action      From
--                         ------      ----
Nginx Full                 ALLOW       Anywhere
OpenSSH                    ALLOW       Anywhere
Nginx Full (v6)            ALLOW       Anywhere (v6)
OpenSSH (v6)               ALLOW       Anywhere (v6)
```

---

## 2. Configuracion de PostgreSQL

### 2.1 Iniciar y habilitar el servicio

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2.2 Crear usuario y base de datos

```bash
# Acceder como usuario postgres
sudo -u postgres psql
```

Dentro del shell de PostgreSQL:

```sql
-- Crear usuario
CREATE USER codeacademy WITH PASSWORD 'C0d3Ac4d3my_Pr0d_2026';

-- Crear base de datos
CREATE DATABASE codeacademy OWNER codeacademy;

-- Configurar parametros del usuario
ALTER ROLE codeacademy SET client_encoding TO 'utf8';
ALTER ROLE codeacademy SET default_transaction_isolation TO 'read committed';
ALTER ROLE codeacademy SET timezone TO 'America/Bogota';

-- Otorgar privilegios
GRANT ALL PRIVILEGES ON DATABASE codeacademy TO codeacademy;

-- Salir
\q
```

### 2.3 Verificar conexion

```bash
psql -U codeacademy -h localhost -d codeacademy
# Ingrese la contrasena cuando se solicite
```

### 2.4 Datos de la base de datos

| Parametro | Valor |
|-----------|-------|
| **Motor** | PostgreSQL 16 |
| **Nombre BD** | `codeacademy` |
| **Usuario** | `codeacademy` |
| **Host** | `localhost` |
| **Puerto** | `5432` |
| **Encoding** | UTF-8 |
| **Timezone** | America/Bogota |

---

## 3. Configuracion de la Aplicacion Django

### 3.1 Clonar el repositorio

```bash
mkdir -p /opt/codeacademy
cd /opt/codeacademy
git clone https://github.com/sergio001g/CodeAcademy_bakend.git
cd CodeAcademy_bakend
```

**Ubicacion del proyecto en el servidor:** `/opt/codeacademy/CodeAcademy_bakend/`

### 3.2 Crear entorno virtual e instalar dependencias

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install django-cors-headers
```

**Dependencias principales (requirements.txt):**

| Paquete | Version | Funcion |
|---------|---------|---------|
| Django | 4.2 | Framework web |
| djangorestframework | 3.14.0 | API REST |
| djangorestframework-simplejwt | 5.3.0 | Autenticacion JWT |
| django-filter | 23.2 | Filtros en endpoints |
| drf-spectacular | 0.27.2 | Documentacion Swagger/ReDoc |
| psycopg2-binary | 2.9.6 | Conector PostgreSQL |
| python-dotenv | 1.0.0 | Variables de entorno |
| Pillow | >=10.0.0 | Manejo de imagenes |
| gunicorn | 21.2.0 | Servidor WSGI |
| django-cors-headers | Latest | Soporte CORS para la API |

### 3.3 Configuracion de Variables de Entorno (.env)

Se creo el archivo `.env` en la raiz del proyecto (`/opt/codeacademy/CodeAcademy_bakend/.env`):

```env
SECRET_KEY=xK9mP2nQ7rS4tU8vW1xY3zA5bC7dE9fG2hJ4kL6mN8pR0sT
DEBUG=False
ALLOWED_HOSTS=159.223.133.69,codeacademy-api.uaeftt-ute.site,localhost,127.0.0.1

# Base de datos PostgreSQL
POSTGRES_DB=codeacademy
POSTGRES_USER=codeacademy
POSTGRES_PASSWORD=C0d3Ac4d3my_Pr0d_2026
DB_HOST=localhost
DB_PORT=5432
```

**Explicacion de las variables:**

| Variable | Descripcion |
|----------|-------------|
| `SECRET_KEY` | Clave secreta de Django para criptografia y sesiones |
| `DEBUG` | `False` en produccion (no muestra errores detallados) |
| `ALLOWED_HOSTS` | Dominios/IPs permitidos para acceder al servidor |
| `POSTGRES_DB` | Nombre de la base de datos PostgreSQL |
| `POSTGRES_USER` | Usuario de la base de datos |
| `POSTGRES_PASSWORD` | Contrasena de la base de datos |
| `DB_HOST` | Host de la base de datos (localhost = misma maquina) |
| `DB_PORT` | Puerto de PostgreSQL (por defecto 5432) |

### 3.4 Modificaciones a settings.py para produccion

Se agregaron las siguientes configuraciones al archivo `core/settings.py`:

```python
# Archivos estaticos
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Archivos media (subidos por usuarios)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CORS - Permite acceso desde cualquier origen
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
```

Tambien se agrego `corsheaders` a `INSTALLED_APPS` y `CorsMiddleware` a `MIDDLEWARE`.

### 3.5 Ejecutar migraciones y configuracion inicial

```bash
cd /opt/codeacademy/CodeAcademy_bakend
source venv/bin/activate

# Aplicar migraciones de la base de datos
python manage.py migrate --noinput

# Crear roles (Usuario y Administrador) y superusuario inicial
python manage.py configurar_roles --email admin@codeacademy.com --password admin123

# Recopilar archivos estaticos para Nginx
python manage.py collectstatic --noinput
```

**Migraciones aplicadas:**
- `contenttypes` (2 migraciones)
- `auth` (12 migraciones)
- `apps` (2 migraciones - modelos personalizados)
- `admin` (3 migraciones)
- `sessions` (1 migracion)
- **Total: 20 migraciones**

### 3.6 Crear superusuario adicional (Profesor)

```bash
cd /opt/codeacademy/CodeAcademy_bakend
source venv/bin/activate
python manage.py shell -c "
from apps.models import User
from django.contrib.auth.models import Group
u = User.objects.create_superuser(email='admin', password='Admin1234!', first_name='Profesor', last_name='Admin')
grupo_admin, _ = Group.objects.get_or_create(name='Administrador')
u.groups.add(grupo_admin)
print('Superusuario creado')
"
```

---

## 4. Configuracion de Gunicorn

### 4.1 Archivo de Socket (systemd)

Se creo `/etc/systemd/system/gunicorn.socket`:

```ini
[Unit]
Description=gunicorn socket para CodeAcademy

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target
```

### 4.2 Archivo de Servicio (systemd)

Se creo `/etc/systemd/system/gunicorn.service`:

```ini
[Unit]
Description=Gunicorn daemon para CodeAcademy Backend
Requires=gunicorn.socket
After=network.target postgresql.service

[Service]
User=root
Group=www-data
WorkingDirectory=/opt/codeacademy/CodeAcademy_bakend
ExecStart=/opt/codeacademy/CodeAcademy_bakend/venv/bin/gunicorn \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile /var/log/gunicorn/error.log \
    --workers 3 \
    --bind unix:/run/gunicorn.sock \
    core.wsgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Parametros de Gunicorn:**

| Parametro | Valor | Descripcion |
|-----------|-------|-------------|
| `workers` | 3 | Numero de procesos worker (2 x CPU + 1) |
| `bind` | `unix:/run/gunicorn.sock` | Comunicacion con Nginx via socket Unix |
| `Restart` | always | Se reinicia automaticamente si falla |
| `access-logfile` | `/var/log/gunicorn/access.log` | Log de accesos |
| `error-logfile` | `/var/log/gunicorn/error.log` | Log de errores |

### 4.3 Habilitar y arrancar Gunicorn

```bash
# Crear directorio de logs
mkdir -p /var/log/gunicorn

# Recargar systemd
systemctl daemon-reload

# Iniciar y habilitar al arranque
systemctl start gunicorn.socket
systemctl enable gunicorn.socket
systemctl start gunicorn
systemctl enable gunicorn

# Verificar estado
systemctl status gunicorn
```

### 4.4 Verificar que el socket existe

```bash
file /run/gunicorn.sock
# Debe mostrar: /run/gunicorn.sock: socket
```

---

## 5. Configuracion de Nginx

### 5.1 Configuracion del sitio

Se creo `/etc/nginx/sites-available/codeacademy` (modificado automaticamente por Certbot para HTTPS):

```nginx
server {
    server_name codeacademy-api.uaeftt-ute.site 159.223.133.69;

    client_max_body_size 10M;

    # Archivos estaticos servidos directamente por Nginx
    location /static/ {
        alias /opt/codeacademy/CodeAcademy_bakend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Archivos media servidos directamente por Nginx
    location /media/ {
        alias /opt/codeacademy/CodeAcademy_bakend/media/;
        expires 30d;
    }

    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }

    # Proxy reverso a Gunicorn
    location / {
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    # SSL configurado por Certbot
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/codeacademy-api.uaeftt-ute.site/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/codeacademy-api.uaeftt-ute.site/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

# Redireccion HTTP a HTTPS
server {
    if ($host = codeacademy-api.uaeftt-ute.site) {
        return 301 https://$host$request_uri;
    }

    listen 80;
    server_name codeacademy-api.uaeftt-ute.site 159.223.133.69;
    return 404;
}
```

### 5.2 Habilitar el sitio

```bash
# Crear enlace simbolico
ln -sf /etc/nginx/sites-available/codeacademy /etc/nginx/sites-enabled/

# Eliminar sitio default
rm -f /etc/nginx/sites-enabled/default

# Verificar configuracion
nginx -t

# Reiniciar Nginx
systemctl restart nginx
systemctl enable nginx
```

### 5.3 Configuracion HTTPS con Let's Encrypt

```bash
# Instalar Certbot
apt install -y certbot python3-certbot-nginx

# Obtener certificado SSL y configurar Nginx automaticamente
certbot --nginx -d codeacademy-api.uaeftt-ute.site \
    --non-interactive --agree-tos \
    --email admin@codeacademy.com --redirect

# Verificar auto-renovacion
certbot renew --dry-run
```

**Datos del certificado SSL:**

| Parametro | Valor |
|-----------|-------|
| **Emisor** | Let's Encrypt |
| **Dominio** | `codeacademy-api.uaeftt-ute.site` |
| **Certificado** | `/etc/letsencrypt/live/codeacademy-api.uaeftt-ute.site/fullchain.pem` |
| **Clave privada** | `/etc/letsencrypt/live/codeacademy-api.uaeftt-ute.site/privkey.pem` |
| **Expiracion** | 2026-09-26 |
| **Auto-renovacion** | Configurada (certbot.timer) |
| **Redireccion HTTP a HTTPS** | Automatica |

---

## 6. Arquitectura del Despliegue

```
                    +----------------------------------------+
                    |        INTERNET                        |
                    |   codeacademy-api.uaeftt-ute.site      |
                    +------------------+---------------------+
                                       |
                              Puerto 443 (HTTPS)
                              Puerto 80 -> Redirige a 443
                                       |
                    +------------------v---------------------+
                    |             NGINX                      |
                    |        (Reverse Proxy)                 |
                    |   SSL/TLS (Let's Encrypt)              |
                    |   Sirve archivos estaticos             |
                    +------------------+---------------------+
                                       |
                              /run/gunicorn.sock
                              (Socket Unix)
                                       |
                    +------------------v---------------------+
                    |           GUNICORN                     |
                    |        (Servidor WSGI)                 |
                    |        3 Workers                       |
                    +------------------+---------------------+
                                       |
                    +------------------v---------------------+
                    |      DJANGO REST FRAMEWORK             |
                    |       (CodeAcademy API)                |
                    |   JWT Auth - Swagger - ReDoc           |
                    +------------------+---------------------+
                                       |
                    +------------------v---------------------+
                    |          POSTGRESQL 16                  |
                    |        (Base de Datos)                 |
                    |     Puerto 5432 (localhost)            |
                    +----------------------------------------+
```

---

## 7. Stack Tecnologico

| Componente | Tecnologia | Version |
|------------|-----------|---------|
| **Sistema Operativo** | Ubuntu | 24.04 LTS |
| **Servidor Web** | Nginx | 1.24.x |
| **Servidor WSGI** | Gunicorn | 21.2.0 |
| **Framework** | Django | 4.2 |
| **API Framework** | Django REST Framework | 3.14.0 |
| **Base de Datos** | PostgreSQL | 16.x |
| **Documentacion API** | drf-spectacular (Swagger/ReDoc) | 0.27.2 |
| **Autenticacion** | JWT (Simple JWT) | 5.3.0 |
| **Certificado SSL** | Let's Encrypt (Certbot) | 2.9.x |
| **CORS** | django-cors-headers | Latest |
| **Python** | Python | 3.12.x |

---

## 8. Endpoints de la API

### Autenticacion

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Registro de nuevos usuarios |
| POST | `/api/auth/login/` | Inicio de sesion (devuelve token JWT) |
| POST | `/api/auth/token/refresh/` | Refrescar token JWT expirado |

### Endpoints publicos (no requieren autenticacion para GET)

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET/POST | `/api/categories/` | Listar y crear categorias |
| GET/POST | `/api/subcategories/` | Listar y crear subcategorias |
| GET/POST | `/api/courses/` | Listar y crear cursos |
| GET/POST | `/api/lessons/` | Listar y crear lecciones |
| GET/POST | `/api/reviews/` | Listar y crear resenas |
| GET/POST | `/api/quizzes/` | Listar y crear quizzes |
| GET/POST | `/api/questions/` | Listar y crear preguntas |
| GET/POST | `/api/answers/` | Listar y crear respuestas |
| GET/POST | `/api/discussion-forums/` | Foros de discusion |
| GET/POST | `/api/forum-posts/` | Posts en foros |
| GET/POST | `/api/forum-comments/` | Comentarios en foros |
| GET/POST | `/api/tags/` | Listar y crear etiquetas |
| GET/POST | `/api/course-tags/` | Etiquetas de cursos |

### Endpoints protegidos (requieren token JWT)

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| GET/POST | `/api/users/` | Listar y crear usuarios |
| GET/POST | `/api/enrollments/` | Listar y crear inscripciones |
| GET/POST | `/api/certificates/` | Listar y crear certificados |
| GET/POST | `/api/progress/` | Listar y actualizar progreso |
| GET/POST | `/api/quiz-attempts/` | Listar intentos de quiz |
| GET/POST | `/api/quiz-answers/` | Listar respuestas de quiz |
| GET/POST | `/api/wishlist/` | Lista de deseos |

> Para acceder a los endpoints protegidos, primero iniciar sesion en `/api/auth/login/` para obtener un token JWT, y luego enviar el token en el header `Authorization: Bearer <token>`.

> Para la documentacion completa e interactiva de todos los endpoints, visitar:
> - **Swagger UI:** https://codeacademy-api.uaeftt-ute.site/api/docs/
> - **ReDoc:** https://codeacademy-api.uaeftt-ute.site/api/docs/redoc/

---

## 9. Comandos Utiles de Administracion

### Ver logs

```bash
# Logs de Gunicorn
journalctl -u gunicorn -f
tail -f /var/log/gunicorn/access.log
tail -f /var/log/gunicorn/error.log

# Logs de Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Logs de PostgreSQL
tail -f /var/log/postgresql/postgresql-16-main.log
```

### Reiniciar servicios

```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
sudo systemctl restart postgresql
```

### Ver estado de servicios

```bash
sudo systemctl status gunicorn
sudo systemctl status nginx
sudo systemctl status postgresql
```

### Actualizar la aplicacion (pull de cambios)

```bash
cd /opt/codeacademy/CodeAcademy_bakend
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
sudo systemctl restart gunicorn
```

### Renovar certificado SSL

```bash
# Renovacion manual (normalmente es automatica)
sudo certbot renew

# Verificar auto-renovacion
sudo certbot renew --dry-run
```

---

## 10. Estructura de Archivos en el Servidor

```
/opt/codeacademy/CodeAcademy_bakend/
├── .env                    # Variables de entorno (produccion)
├── manage.py               # Script de gestion de Django
├── requirements.txt        # Dependencias de Python
├── core/                   # Configuracion principal de Django
│   ├── settings.py         # Configuraciones del proyecto
│   ├── urls.py             # Rutas principales
│   └── wsgi.py             # Punto de entrada WSGI (Gunicorn)
├── apps/                   # Aplicacion principal (modelos, vistas, serializers)
│   ├── models.py           # Modelos de datos
│   ├── views.py            # Vistas de la API
│   ├── serializers.py      # Serializadores
│   ├── urls.py             # Rutas de la API
│   └── management/         # Comandos personalizados (configurar_roles)
├── templates/              # Plantillas HTML
├── venv/                   # Entorno virtual Python
├── staticfiles/            # Archivos estaticos recopilados (collectstatic)
└── media/                  # Archivos subidos por usuarios

/etc/systemd/system/
├── gunicorn.socket         # Socket systemd de Gunicorn
└── gunicorn.service        # Servicio systemd de Gunicorn

/etc/nginx/sites-available/
└── codeacademy             # Configuracion de Nginx

/etc/letsencrypt/live/codeacademy-api.uaeftt-ute.site/
├── fullchain.pem           # Certificado SSL completo
└── privkey.pem             # Clave privada SSL
```
