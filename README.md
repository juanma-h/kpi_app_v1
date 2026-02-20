📊 KPI E-commerce Monitor API

Sistema backend para monitoreo estructurado de productividad en equipos de E-commerce.

Permite autenticación segura, control de turnos laborales, gestión de sesiones activas y prepara la base para captura futura de eventos de actividad.

🧠 Objetivo del Proyecto

Construir una plataforma escalable que permita:

Validar conexión real de empleados

Controlar inicio y fin de turnos

Evitar doble turno simultáneo

Establecer base para monitoreo de actividad

Generar métricas KPI confiables

Diseñado con enfoque profesional y arquitectura escalable.

🚀 Stack Tecnológico

Python 3.13

FastAPI

SQLAlchemy (ORM)

PostgreSQL

Alembic (migraciones)

JWT (python-jose)

Passlib + Bcrypt

Uvicorn

🏗 Arquitectura del Proyecto
backend/
│
├── app/
│   ├── core/          # Configuración, seguridad y dependencias
│   ├── db/            # Base declarativa y sesión de BD
│   ├── models/        # Modelos SQLAlchemy
│   ├── routers/       # Endpoints organizados por módulo
│   ├── schemas/       # Esquemas Pydantic (validación)
│   ├── seed_admin.py  # Script de creación de usuario admin
│   └── main.py        # Punto de entrada FastAPI
│
├── alembic/           # Migraciones
├── .env               # Variables de entorno
└── requirements.txt

🔐 Modelo de Seguridad

Autenticación basada en JWT

OAuth2PasswordBearer

Roles definidos (ADMIN / EMPLOYEE)

Validación de turno abierto

Regla anti doble turno activo

📦 Instalación del Proyecto
1️⃣ Clonar repositorio
git clone <URL_DEL_REPOSITORIO>
cd backend

2️⃣ Crear entorno virtual

Windows:

python -m venv .venv
.venv\Scripts\activate


Mac / Linux:

python -m venv .venv
source .venv/bin/activate

3️⃣ Instalar dependencias
pip install -r requirements.txt

🗄 Configuración Base de Datos

Crear base de datos PostgreSQL:

CREATE DATABASE kpi_app;


Crear archivo .env en la raíz de backend:

DATABASE_URL=postgresql+psycopg2://postgres:123456789@localhost:5432/kpi_app
JWT_SECRET=supersecretkey
JWT_ALG=HS256
ACCESS_TOKEN_EXPIRE_MIN=60

🧱 Migraciones

Generar migración inicial:

alembic revision --autogenerate -m "initial migration"


Aplicar migraciones:

alembic upgrade head

👤 Crear Usuario Administrador
python -m app.seed_admin


Credenciales por defecto:

Email:

admin@kpi.com


Password:

Admin123*

▶️ Ejecutar Servidor
uvicorn app.main:app --reload


Acceder a documentación Swagger:

http://127.0.0.1:8000/docs

🔐 Autenticación

POST /auth/login

Usar botón Authorize

Probar /auth/me

Sistema basado en JWT Bearer Token.

⏱ Control de Turnos (Semana 1)
Iniciar Turno
POST /shifts/start


Crea Shift OPEN

Crea Session OPEN

Valida que no exista turno activo previo

Turno Actual
GET /shifts/current


Devuelve turno activo si existe

Finalizar Turno
POST /shifts/end


Cierra Shift

Cierra Session

Guarda timestamp de cierre

📊 Modelo de Datos (Semana 1)

Relación principal:

User
 └── Shift
       └── Session

User

id

name

email

password_hash

role

is_active

Shift

id

user_id

start_at

end_at

status

Session

id

user_id

shift_id

start_at

end_at

status

device_label

📅 Roadmap
✅ Semana 1

JWT Authentication

Control de turnos

Control de sesiones

Validación anti doble turno

🔜 Semana 2

Allowlist de plataformas

Ingesta de eventos

Auditoría básica de actividad

🔜 Futuro

Extensión de navegador

Dashboard de métricas

KPIs automatizados

Alertas por inactividad

🧠 Enfoque de Desarrollo

Arquitectura pensada para:

Escalabilidad futura

Separación por capas

Seguridad desde diseño

Monitoreo productivo profesional

Posible integración con frontend React

⚠️ Estado del Proyecto

En desarrollo activo.
No preparado aún para producción.
Fase actual: Backend Core funcional.

👨‍💻 Autor

Juan Manuel
Software Engineering Student
Proyecto académico + profesional en evolución