# Roda — Backend (Simulador de crédito)

API REST en Flask + PostgreSQL para simular créditos de movilidad eléctrica y registrar solicitudes.

## Tecnologías

- **Python 3.12+**
- **Flask 3.1**
- **SQLAlchemy 2.x** + **Flask-SQLAlchemy**
- **Flask-Migrate** (Alembic)
- **psycopg 3** (driver PostgreSQL moderno)
- **Pydantic 2** (validaciones)
- **Gunicorn** (producción)

## Estructura

```
backend/
├── app/
│   ├── __init__.py          # App factory
│   ├── config.py            # Configuración por entorno
│   ├── extensions.py        # Instancias de db, migrate, cors
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Schemas Pydantic
│   ├── routes/
│   │   ├── simulation.py    # POST /api/simulate
│   │   └── application.py   # POST /api/applications
│   └── services/
│       └── credit_service.py # Lógica de cálculo (sistema francés)
├── tests/
├── migrations/              # Generado por flask db init
├── requirements.txt
├── run.py                   # Entry point
├── Procfile                 # Deploy
├── render.yaml              # Render Blueprint
└── .env.example
```

## Variables de entorno

Copia `.env.example` a `.env` y ajusta:

| Variable | Descripción | Default |
|---|---|---|
| `FLASK_APP` | Módulo de entrada | `run.py` |
| `FLASK_ENV` | `development` o `production` | `development` |
| `SECRET_KEY` | Clave de Flask | (cambiar en prod) |
| `DATABASE_URL` | URL de PostgreSQL | `postgresql+psycopg://...` |
| `ANNUAL_INTEREST_RATE` | Tasa EA (decimal) | `0.18` |
| `CORS_ORIGINS` | Orígenes separados por coma | `http://localhost:5173` |
| `PORT` | Puerto del servidor | `5000` |

## Instalación local

### 1. Pre-requisitos
- Python 3.12+ (`python --version`)
- PostgreSQL 16/17 corriendo localmente

### 2. Clonar y crear entorno virtual

```bash
git clone <tu-repo-backend>
cd roda-credit-backend
python -m venv venv
source venv/bin/activate    # Linux/Mac
# venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 3. Crear base de datos PostgreSQL

```bash
# Conectarse a psql como superuser
psql -U postgres

# Dentro de psql:
CREATE DATABASE roda_db;
CREATE USER roda_user WITH PASSWORD 'roda_pass';
GRANT ALL PRIVILEGES ON DATABASE roda_db TO roda_user;
\c roda_db
GRANT ALL ON SCHEMA public TO roda_user;
\q
```

### 4. Configurar `.env`

```bash
cp .env.example .env
# Editar DATABASE_URL si tus credenciales son distintas
```

### 5. Inicializar migraciones y crear tablas

```bash
export FLASK_APP=run.py        # Linux/Mac
# set FLASK_APP=run.py         # Windows CMD

flask db init                  # Solo la primera vez
flask db migrate -m "initial schema"
flask db upgrade
```

### 6. Correr el servidor

```bash
flask run --debug
# o:
python run.py
```

API disponible en `http://localhost:5000`.

### 7. Correr tests

```bash
pip install pytest
pytest -v
```

## Endpoints

### `GET /health`
Healthcheck. Devuelve `{"status": "healthy"}`.

### `POST /api/simulate`
Calcula la simulación sin persistir nada.

**Body:**
```json
{
  "vehicle_type": "motorcycle",
  "vehicle_value": 8000000,
  "down_payment": 1500000,
  "term_months": 24
}
```

**Response 200:**
```json
{
  "summary": {
    "vehicle_type": "motorcycle",
    "vehicle_value": 8000000,
    "down_payment": 1500000,
    "term_months": 24,
    "financed_amount": 6500000.00,
    "monthly_payment": 322874.55,
    "total_interest": 1248989.20,
    "total_to_pay": 7748989.20,
    "annual_interest_rate": 0.18
  },
  "schedule": [
    {"number": 1, "payment": 322874.55, "interest": 90227.41, "principal": 232647.14, "balance": 6267352.86},
    ...
  ]
}
```

### `POST /api/applications`
Persiste una solicitud completa en PostgreSQL.

**Body:** mismos campos de `/simulate` + `first_name`, `last_name`, `email`, `phone`, `city`.

**Response 201:**
```json
{
  "message": "Solicitud registrada exitosamente",
  "application": { "id": 1, "...": "..." }
}
```

### `GET /api/applications`
Lista las últimas solicitudes (útil para verificar persistencia).

## Validaciones

- `vehicle_value` ≥ $500.000 COP
- `down_payment` < `vehicle_value` (debe haber monto a financiar)
- `term_months` entre 6 y 60
- `email` con formato válido (Pydantic `EmailStr`)
- `phone` solo dígitos
- Todos los campos obligatorios

## Lógica de cálculo

Sistema francés (cuota fija). La tasa efectiva anual (EA) se convierte a tasa mensual equivalente:

```
i_mensual = (1 + EA)^(1/12) - 1
cuota = financiado · (i · (1+i)^n) / ((1+i)^n - 1)
```

Donde `n` = plazo en meses. La última cuota se ajusta para que el saldo final sea exactamente 0 (corrección de redondeo).

## Decisiones técnicas

- **Pydantic** sobre Marshmallow por mejor DX y mensajes de error claros.
- **psycopg 3** sobre `psycopg2-binary` por mejor performance y soporte async futuro.
- **App factory** para facilitar testing y múltiples entornos.
- **`Numeric(14, 2)`** en montos: precisión decimal exacta (no `Float`).
- **Recálculo en backend** al registrar solicitud: evita que el cliente envíe valores manipulados.
- **CORS** restringido por env var: en prod solo se acepta el origen del frontend desplegado.
