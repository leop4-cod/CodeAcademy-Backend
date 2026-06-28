
# CodeAcademy Backend

Backend desarrollado para la plataforma **CodeAcademy**, una aplicación web orientada a la gestión de cursos en línea. El proyecto fue implementado con **Django 4.2**, **Django REST Framework** y **PostgreSQL**, siguiendo una arquitectura **REST** que permite la integración con aplicaciones web y móviles.

El sistema ofrece funcionalidades para administrar usuarios, cursos, lecciones, evaluaciones, certificados, foros de discusión y otros recursos relacionados con el aprendizaje en línea. Además, incorpora autenticación mediante **JSON Web Token (JWT)**, control de acceso basado en roles y documentación automática utilizando **Swagger** y **ReDoc**.

---

# Tecnologías utilizadas

- Python 3
- Django 4.2
- Django REST Framework
- PostgreSQL
- Simple JWT
- Docker
- Gunicorn
- Nginx
- drf-spectacular (Swagger y ReDoc)

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

# Características principales

El backend implementa las siguientes funcionalidades:

- Registro de usuarios.
- Inicio de sesión mediante JWT.
- Administración de cursos.
- Gestión de categorías y subcategorías.
- Administración de lecciones.
- Gestión de evaluaciones.
- Inscripción de estudiantes.
- Seguimiento del progreso.
- Emisión de certificados.
- Sistema de reseñas.
- Foros de discusión.
- Gestión de etiquetas para cursos.
- Lista de deseos.
- API completamente documentada.
- Despliegue en VPS utilizando Gunicorn y Nginx.

---

# Modelo de Base de Datos

La aplicación utiliza **PostgreSQL** como gestor de base de datos relacional. El modelo está conformado por **20 tablas**, las cuales representan los principales módulos del sistema.

| Tabla | Descripción |
|--------|-------------|
| **User** | Información de los usuarios registrados. |
| **Category** | Categorías generales de los cursos. |
| **Subcategory** | Subcategorías pertenecientes a una categoría. |
| **Course** | Información principal de cada curso. |
| **Lesson** | Lecciones que conforman un curso. |
| **Enrollment** | Registro de estudiantes inscritos. |
| **Review** | Calificaciones y opiniones de los cursos. |
| **Certificate** | Certificados emitidos al completar un curso. |
| **Progress** | Seguimiento del avance del estudiante. |
| **Quiz** | Evaluaciones de los cursos. |
| **Question** | Preguntas de una evaluación. |
| **Answer** | Respuestas de las preguntas. |
| **QuizAttempt** | Intentos realizados por un estudiante. |
| **QuizAnswer** | Respuestas registradas durante un intento. |
| **DiscussionForum** | Foros de discusión de cada curso. |
| **ForumPost** | Publicaciones realizadas en un foro. |
| **ForumComment** | Comentarios asociados a una publicación. |
| **Tag** | Etiquetas para clasificar cursos. |
| **CourseTag** | Relación entre cursos y etiquetas. |
| **Wishlist** | Lista de cursos guardados por un usuario. |

## Relaciones implementadas

### One-to-One

- **Certificate → Enrollment**

Cada inscripción puede generar un único certificado cuando el estudiante finaliza el curso.

### One-to-Many

- Category → Subcategory
- Category → Course
- Course → Lesson
- Course → Quiz
- Quiz → Question
- Question → Answer
- DiscussionForum → ForumPost
- ForumPost → ForumComment
- User → Enrollment
- User → Review

### Many-to-Many

- **Course ↔ Tag**

La relación se implementa mediante la tabla **CourseTag**, permitiendo que un curso tenga varias etiquetas y que una etiqueta pueda asociarse a múltiples cursos.

---

# Instalación

## 1. Clonar el repositorio

```bash
git clone https://github.com/sergio001g/CodeAcademy_bakend.git
cd CodeAcademy_bakend
```

## 2. Crear el entorno virtual

```bash
python -m venv venv
```

### Linux / macOS

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

# Configuración

Crear el archivo `.env`.

```bash
cp .env.example .env
```

Variables principales:

```env
POSTGRES_DB=codeacademy
POSTGRES_USER=codeacademy
POSTGRES_PASSWORD=codeacademy
DB_HOST=localhost
```

---

# Migraciones

Crear la estructura de la base de datos.

```bash
python manage.py migrate
```

Crear el usuario administrador.

```bash
python manage.py configurar_roles --email admin@codeacademy.com --password admin123
```

---

# Ejecución con Docker

```bash
docker-compose up --build -d
```

Migraciones:

```bash
docker-compose exec web python manage.py migrate
```

Administrador:

```bash
docker-compose exec web python manage.py configurar_roles --email admin@codeacademy.com --password admin123
```

---

# Autenticación

La API utiliza **JSON Web Token (JWT)**.

## Registro

```http
POST /api/auth/register/
```

```json
{
    "email":"usuario@example.com",
    "password":"miPassword123",
    "first_name":"Juan",
    "last_name":"Pérez"
}
```

## Inicio de sesión

```http
POST /api/auth/login/
```

Respuesta:

```json
{
    "access":"token_jwt",
    "refresh":"refresh_token"
}
```

Para acceder a las rutas protegidas:

```http
Authorization: Bearer <access_token>
```

Renovar token:

```http
POST /api/auth/token/refresh/
```

---

# Recursos disponibles

Todos los módulos implementan operaciones **CRUD (Create, Read, Update y Delete)**.

- Users
- Categories
- Subcategories
- Courses
- Lessons
- Enrollments
- Reviews
- Certificates
- Progress
- Quizzes
- Questions
- Answers
- Quiz Attempts
- Quiz Answers
- Discussion Forums
- Forum Posts
- Forum Comments
- Tags
- Course Tags
- Wishlist

La API permite realizar búsquedas, filtros, ordenamiento y paginación.

Ejemplos:

```http
GET /api/courses/?search=django
GET /api/categories/?search=web
GET /api/enrollments/?ordering=-enrolled_at
```

---

# Roles y permisos

## Usuario

- Consultar cursos y recursos públicos.
- Inscribirse en cursos.
- Crear reseñas.
- Publicar en los foros.
- Comentar publicaciones.
- Administrar únicamente sus propios registros.

## Administrador

- Gestión completa de usuarios.
- Gestión de cursos.
- Gestión de categorías.
- Gestión de certificados.
- Administración de evaluaciones.
- Acceso a todas las operaciones CRUD.

Las rutas protegidas requieren un token JWT válido. Si no existe autenticación, la API responde con **401 Unauthorized**. Cuando el usuario autenticado no tiene permisos suficientes, la respuesta es **403 Forbidden**.

---

# Documentación de la API

La documentación se genera automáticamente mediante **drf-spectacular**.

| Recurso | URL |
|----------|-----|
| Swagger | https://codeacademy-api.uaeftt-ute.site/api/docs/ |
| ReDoc | https://codeacademy-api.uaeftt-ute.site/api/docs/redoc/ |
| OpenAPI Schema | https://codeacademy-api.uaeftt-ute.site/api/schema/ |

También se incluye una colección de **Postman** para facilitar las pruebas de todos los endpoints.

---

# Despliegue

La aplicación fue desplegada en un servidor **VPS** utilizando la siguiente arquitectura:

- Ubuntu Server
- PostgreSQL
- Gunicorn
- Nginx
- Django

Gunicorn ejecuta la aplicación Django mientras que Nginx funciona como proxy inverso, permitiendo exponer la API mediante un dominio público.

---

# Licencia

Este proyecto fue desarrollado con fines académicos para la asignatura correspondiente y puede utilizarse como referencia para proyectos educativos basados en Django y Django REST Framework.
````
