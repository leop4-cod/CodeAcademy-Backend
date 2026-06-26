# CodeAcademy API

API REST para una plataforma de cursos en línea, desarrollada con **Django 4.2** y **Django REST Framework**.

## Información General

- **Nombre del proyecto:** CodeAcademy Backend
- **Descripción:** Sistema de gestión de cursos, lecciones, inscripciones, evaluaciones, foros y certificados con autenticación JWT y roles de usuario.
- **Base de datos:** PostgreSQL (20 tablas relacionadas)
- **Documentación interactiva:** Swagger en `/api/docs/` y ReDoc en `/api/docs/redoc/`

## Instalación Local

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd CodeAcademy_bakend
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con tus credenciales de PostgreSQL.

### 4. Ejecutar con Docker (recomendado)

```bash
docker-compose up --build -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py configurar_roles --email admin@codeacademy.com --password admin123
```

### 5. Ejecutar sin Docker

```bash
export POSTGRES_DB=codeacademy
export POSTGRES_USER=codeacademy
export POSTGRES_PASSWORD=codeacademy
export DB_HOST=localhost
python manage.py migrate
python manage.py configurar_roles --email admin@codeacademy.com --password admin123
python manage.py runserver
```

## Uso de la API

### Registro de usuario

```bash
POST /api/auth/register/
Content-Type: application/json

{
  "email": "usuario@example.com",
  "password": "miPassword123",
  "first_name": "Juan",
  "last_name": "Pérez"
}
```

### Inicio de sesión (JWT)

```bash
POST /api/auth/login/
Content-Type: application/json

{
  "email": "admin@codeacademy.com",
  "password": "admin123"
}
```

Respuesta:

```json
{
  "access": "token_jwt...",
  "refresh": "token_refresh..."
}
```

### Endpoints protegidos

Incluir el header en peticiones que requieran autenticación:

```
Authorization: Bearer <access_token>
```

### Ejemplos de consultas

```bash
GET /api/courses/?search=django&ordering=price&page=1
GET /api/categories/?search=web
GET /api/enrollments/?ordering=-enrolled_at
```

## Roles y Permisos

| Rol | Permisos |
|-----|----------|
| **Usuario** | Consultar recursos, crear inscripciones, reseñas, posts y comentarios propios |
| **Administrador** | CRUD completo, gestión de usuarios y certificados |

## Endpoints Disponibles

### Autenticación
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/auth/register/` | Registro de usuario |
| POST | `/api/auth/login/` | Obtener token JWT |
| POST | `/api/auth/token/refresh/` | Renovar token |

### Recursos (CRUD completo en cada uno)
| Recurso | Ruta base |
|---------|-----------|
| Usuarios | `/api/users/` |
| Categorías | `/api/categories/` |
| Subcategorías | `/api/subcategories/` |
| Cursos | `/api/courses/` |
| Lecciones | `/api/lessons/` |
| Inscripciones | `/api/enrollments/` |
| Reseñas | `/api/reviews/` |
| Certificados | `/api/certificates/` |
| Progreso | `/api/progress/` |
| Quizzes | `/api/quizzes/` |
| Preguntas | `/api/questions/` |
| Respuestas | `/api/answers/` |
| Intentos de quiz | `/api/quiz-attempts/` |
| Respuestas de quiz | `/api/quiz-answers/` |
| Foros | `/api/discussion-forums/` |
| Posts del foro | `/api/forum-posts/` |
| Comentarios | `/api/forum-comments/` |
| Etiquetas | `/api/tags/` |
| Etiquetas de curso | `/api/course-tags/` |
| Lista de deseos | `/api/wishlist/` |

### Documentación
| Ruta | Descripción |
|------|-------------|
| `/api/docs/` | Swagger UI |
| `/api/docs/redoc/` | ReDoc |
| `/api/schema/` | Esquema OpenAPI |

## Despliegue en VPS

### PostgreSQL

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo -u postgres createuser codeacademy --pwprompt
sudo -u postgres createdb codeacademy -O codeacademy
```

### Gunicorn

```bash
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

### Nginx (proxy inverso)

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Modelo de Datos (20 tablas)

1. User | 2. Category | 3. Subcategory | 4. Course | 5. Lesson
6. Enrollment | 7. Review | 8. Certificate | 9. Progress | 10. Quiz
11. Question | 12. Answer | 13. QuizAttempt | 14. QuizAnswer | 15. DiscussionForum
16. ForumPost | 17. ForumComment | 18. Tag | 19. CourseTag | 20. Wishlist

**Relaciones:** One-to-One (Certificate ↔ Enrollment), One-to-Many (FK en múltiples modelos), Many-to-Many (Course ↔ Tag vía CourseTag).

## Colección Postman

Importar `postman_collection.json` con variable `baseUrl = http://localhost:8000/api`.
