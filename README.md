# CodeAcademy API

API REST para la gestión de plataformas de educación en línea: cursos, lecciones, inscripciones, evaluaciones, foros de discusión, certificados y más.

---

# Enlaces del proyecto

| Recurso | URL |
|----------|-----|
| **Repositorio GitHub** | https://github.com/sergio001g/CodeAcademy_bakend |
| **Sitio principal** | https://codeacademy-api.uaeftt-ute.site/ |
| **API REST** | https://codeacademy-api.uaeftt-ute.site/api/ |
| **Swagger** | https://codeacademy-api.uaeftt-ute.site/api/docs/ |
| **ReDoc** | https://codeacademy-api.uaeftt-ute.site/api/docs/redoc/ |
| **Panel de administración** | https://codeacademy-api.uaeftt-ute.site/admin/ |

---

## Descripción del sistema

CodeAcademy API es un backend desarrollado con **Django REST Framework** que permite a instituciones educativas, tutores y estudiantes gestionar integralmente la experiencia de aprendizaje digital. El sistema ofrece:

- **Autenticación segura con JWT** (access + refresh tokens)
- **Roles de usuario y control de acceso**: Usuario y Administrador (con soporte para perfiles de Estudiante y Profesor)
- **CRUD completo** de cursos, lecciones, categorías, subcategorías y etiquetas
- **Módulo de evaluaciones (Quizzes)** con gestión de preguntas, respuestas, intentos y puntajes
- **Sistema de foros de discusión** con temas (posts) y respuestas (comentarios) en vivo por curso
- **Seguimiento de progreso educativo**, lista de deseos (wishlist) y calificaciones/reseñas de cursos
- **Emisión automática de certificados** de finalización de curso
- **Despliegue en producción** optimizado con **Gunicorn + Nginx + PostgreSQL** en servidor VPS (DigitalOcean)

---

## Instalación local

### 1. Clonar el repositorio

```bash
git clone https://github.com/sergio001g/CodeAcademy_bakend.git
cd CodeAcademy_bakend
```

### 2. Crear el entorno virtual

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Contenido mínimo del `.env`:

```env
# Django
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=

# CORS
CORS_ALLOW_ALL_ORIGINS=
```

### 5. Ejecutar migraciones

```bash
python manage.py makemigrations users courses enrollments reviews quizzes forums
python manage.py migrate
```

### 6. Configurar roles y crear superusuario administrador

```bash
python manage.py configurar_roles
```

### 7. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

La API estará disponible en `http://localhost:8000/api/` y la documentación interactiva en `http://localhost:8000/api/docs/`.

---

## Despliegue en producción (DigitalOcean VPS)

### Requisitos previos

- VM Ubuntu 24.04 / 22.04 en DigitalOcean
- Puerto 80 y 443 abiertos en el Firewall

### 1. Configuración del VPS

```bash
# Crear usuario del sistema
sudo adduser codeacademy
sudo usermod -aG www-data codeacademy

# Clonar el proyecto
sudo mkdir -p /opt/codeacademy
sudo chown codeacademy:www-data /opt/codeacademy
cd /opt/codeacademy
git clone https://github.com/sergio001g/CodeAcademy_bakend.git CodeAcademy_bakend
cd CodeAcademy_bakend

# Crear entorno virtual e instalar dependencias
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install django-cors-headers whitenoise
```

### 2. Configuración de PostgreSQL

```bash
sudo apt install -y postgresql postgresql-contrib
sudo -u postgres psql

-- En psql:
CREATE DATABASE codeacademy_db;
CREATE USER codeacademy_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE codeacademy_db TO codeacademy_user;
\q
```

### 3. Configuración de Gunicorn

Crear `/etc/systemd/system/gunicorn.service`:

```ini
[Unit]
Description=Gunicorn daemon para CodeAcademy Backend
After=network.target postgresql.service

[Service]
User=codeacademy
Group=www-data
WorkingDirectory=/opt/codeacademy/CodeAcademy_bakend
ExecStart=/opt/codeacademy/CodeAcademy_bakend/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/run/gunicorn.sock \
          --access-logfile /var/log/gunicorn/access.log \
          --error-logfile /var/log/gunicorn/error.log \
          core.wsgi:application
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
sudo mkdir -p /var/log/gunicorn
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

### 4. Configuración de Nginx

```bash
sudo apt install -y nginx
```

Crear `/etc/nginx/sites-available/codeacademy`:

```nginx
server {
    listen 80;
    server_name codeacademy-api.uaeftt-ute.site 159.223.133.69;

    client_max_body_size 10M;

    location /static/ {
        alias /opt/codeacademy/CodeAcademy_bakend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /opt/codeacademy/CodeAcademy_bakend/media/;
        expires 30d;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
        proxy_read_timeout 90;
        proxy_connect_timeout 90;
    }
}
```

```bash
sudo ln -sf /etc/nginx/sites-available/codeacademy /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## Uso de la API

### Obtención de token JWT
`POST /api/auth/login/`

```json
{
  "email": "admin@codeacademy.com",
  "password": "tu_password"
}
```

Respuesta:

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Uso de endpoints protegidos
Incluye el token en el header de cada petición:

```http
Authorization: Bearer <TU_ACCESS_TOKEN>
```

### Ejemplos de peticiones

**Registrar usuario:**
```bash
curl -X POST https://codeacademy-api.uaeftt-ute.site/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "usuario@codeacademy.com", "password": "tu_password", "first_name": "Usuario", "last_name": "Ejemplo"}'
```

**Listar cursos (con búsqueda, ordenamiento y paginación):**
```bash
curl "https://codeacademy-api.uaeftt-ute.site/api/courses/?search=django&ordering=price&page=1"
```

**Crear un curso:**
```bash
curl -X POST https://codeacademy-api.uaeftt-ute.site/api/courses/ \
  -H "Authorization: Bearer TU_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category": 1,
    "teacher": 1,
    "title": "Curso Profesional de Django REST Framework",
    "description": "Domina la creación de APIs profesionales",
    "price": "29.99",
    "is_published": true
  }'
```

**Refrescar token:**
```bash
curl -X POST https://codeacademy-api.uaeftt-ute.site/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "TU_REFRESH_TOKEN"}'
```

---

## Endpoints

Todos los endpoints usan el prefijo `/api/`. Los endpoints protegidos requieren el header `Authorization: Bearer <token>`.

### 🔐 Autenticación
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Registrar nuevo usuario |
| POST | `/api/auth/login/` | Iniciar sesión y obtener tokens JWT |
| POST | `/api/auth/token/refresh/` | Refrescar access token |

### 👤 Usuarios (`apps/users`)
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/users/` | Listar usuarios (Search & Ordering) |
| POST | `/api/users/` | Crear usuario (Admin) |
| GET | `/api/users/{id}/` | Detalle de usuario |
| PUT / PATCH | `/api/users/{id}/` | Actualizar usuario |
| DELETE | `/api/users/{id}/` | Eliminar usuario |

### 📚 Categorías y Subcategorías (`apps/courses`)
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET / POST | `/api/categories/` | Listar y crear categorías |
| GET / PUT / DELETE | `/api/categories/{id}/` | Detalle, actualizar y eliminar categoría |
| GET / POST | `/api/subcategories/` | Listar y crear subcategorías |
| GET / PUT / DELETE | `/api/subcategories/{id}/` | Detalle, actualizar y eliminar subcategoría |

### 🎓 Cursos y Lecciones (`apps/courses`)
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET / POST | `/api/courses/` | Listar y crear cursos (Filtros: categoría, profesor, precio) |
| GET / PUT / DELETE | `/api/courses/{id}/` | Detalle, actualizar y eliminar curso |
| GET / POST | `/api/lessons/` | Listar y crear lecciones por curso |
| GET / PUT / DELETE | `/api/lessons/{id}/` | Detalle, actualizar y eliminar lección |

### 🏷️ Etiquetas (`apps/courses`)
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET / POST | `/api/tags/` | Listar y crear etiquetas |
| GET / PUT / DELETE | `/api/tags/{id}/` | Detalle, actualizar y eliminar etiqueta |
| GET / POST | `/api/course-tags/` | Asignar etiquetas a cursos |

### 📝 Inscripciones y Progreso (`apps/enrollments`)
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET / POST | `/api/enrollments/` | Listar e inscribirse a un curso |
| GET / DELETE | `/api/enrollments/{id}/` | Detalle y cancelar inscripción |
| GET / POST | `/api/progress/` | Registrar y listar avance de lecciones |
| GET / POST / DELETE | `/api/wishlist/` | Gestionar lista de deseos de cursos |

### ⭐ Reseñas y Certificados (`apps/reviews`)
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET / POST | `/api/reviews/` | Listar y crear calificaciones/reseñas (1-5 estrellas) |
| GET / PUT / DELETE | `/api/reviews/{id}/` | Detalle, editar y eliminar reseña |
| GET / POST | `/api/certificates/` | Consultar y emitir certificados de finalización |

### 📊 Evaluaciones (Quizzes) (`apps/quizzes`)
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET / POST | `/api/quizzes/` | Listar y crear exámenes de curso |
| GET / POST | `/api/questions/` | Gestionar preguntas del examen |
| GET / POST | `/api/answers/` | Gestionar opciones de respuesta |
| GET / POST | `/api/quiz-attempts/` | Registrar e historial de intentos del estudiante |
| GET / POST | `/api/quiz-answers/` | Registrar respuestas seleccionadas por el estudiante |

### 💬 Foros de Discusión (`apps/forums`)
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET / POST | `/api/discussion-forums/` | Listar y crear foros por curso |
| GET / POST | `/api/forum-posts/` | Listar y crear publicaciones/dudas |
| GET / POST | `/api/forum-comments/` | Comentar en las publicaciones del foro |

---

## Stack tecnológico

- **Backend:** Python 3.12 / 3.10, Django 4.2, Django REST Framework
- **Base de datos:** PostgreSQL 15 / 16
- **Autenticación:** JWT (`djangorestframework-simplejwt`)
- **Documentación API:** `drf-spectacular` (Swagger UI & ReDoc)
- **Servidor WSGI:** Gunicorn
- **Proxy inverso:** Nginx
- **Infraestructura:** DigitalOcean VPS (Ubuntu Linux)
