# 📊 KPI E-commerce Monitor API

Sistema backend para monitorización de productividad en operaciones de E-commerce.

Permite:
- Autenticación segura con JWT
- Control de turnos (shift start / end)
- Control de sesiones activas
- Base para captura futura de eventos de navegación y actividad

Proyecto desarrollado como arquitectura escalable en FastAPI + PostgreSQL.

---

## 🚀 Stack Tecnológico

- Python 3.13
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL
- Alembic (migraciones)
- JWT (python-jose)
- Passlib + Bcrypt
- Uvicorn

---

## 🏗 Arquitectura del Proyecto

backend/
│
├── app/
│ ├── core/ # Configuración, seguridad y dependencias
│ ├── db/ # Base declarativa y sesión
│ ├── models/ # Modelos SQLAlchemy
│ ├── routers/ # Endpoints agrupados por módulo
│ ├── schemas/ # Esquemas Pydantic
│ ├── seed_admin.py # Script de creación de admin
│ └── main.py # Punto de entrada FastAPI
│
├── alembic/ # Migraciones
├── .env # Variables de entorno
└── requirements.txt


---

## ⚙️ Configuración del Entorno

### 1️⃣ Clonar el repositorio

git clone <url-del-repo>
cd backend

### 2️⃣ Crear entorno virtual

python -m venv .venv

Windows
.venv\Scripts\activate

Mac/Linux
source .venv/bin/activate

### 3️⃣ Instalar dependencias

pip install -r requirements.txt

## 🗄 Configuración de Base de Datos
# rda el script de activacion del entorno virtual .venv\Scripts\activate