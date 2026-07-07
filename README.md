# Handwritten Maths Formula

Handwritten Maths Formula is a full-stack handwritten mathematical expression recognition application. It lets users upload or draw a handwritten equation, sends the image to a FastAPI backend, runs Pix2Tex OCR to generate LaTeX, renders the result in the React frontend with KaTeX, and stores prediction history in PostgreSQL.

The project is organized as a production-style web app:

- **Frontend:** React 19, Vite, Tailwind CSS, React Router, Axios, KaTeX
- **Backend:** FastAPI, SQLAlchemy, Pydantic, Alembic, Pix2Tex
- **Database:** PostgreSQL in Docker, with SQLite/test database support in tests
- **Model path:** Pix2Tex is the active OCR engine; YOLO files remain for research/reference
- **Deployment:** Docker Compose for frontend, backend, database, uploads, and model cache volumes

## Table of Contents

- [Features](#features)
- [Active OCR Architecture](#active-ocr-architecture)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Quick Start with Docker](#quick-start-with-docker)
- [Local Development](#local-development)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Frontend Routes](#frontend-routes)
- [Model Lifecycle](#model-lifecycle)
- [Preprocessing Policy](#preprocessing-policy)
- [Database and Migrations](#database-and-migrations)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Validation Notes](#validation-notes)

## Features

- Upload handwritten mathematical expression images.
- Draw expressions directly in the browser canvas.
- Convert handwriting into render-ready LaTeX.
- Render predicted expressions with KaTeX.
- Persist prediction history.
- Search and paginate history records.
- Delete individual history items.
- Expose backend health and model status endpoints.
- Cache Pix2Tex/Hugging Face model files across Docker rebuilds.
- Keep legacy YOLO-based recognition modules available for experimentation.

## Active OCR Architecture

The production prediction path uses Pix2Tex (`pix2tex.cli.LatexOCR`) as the primary OCR engine:

```text
upload/draw image
  -> backend validation
  -> Pix2Tex-compatible preprocessing
  -> Pix2Tex OCR
  -> LaTeX response
  -> KaTeX rendering
  -> history persistence
```

Legacy YOLO symbol detection, expression parsing, AST generation, and LaTeX generation files remain in the repository for research/reference, but these production endpoints no longer call the YOLO pipeline:

- `POST /api/v1/predict`
- `POST /api/v1/expressions/recognize`
- `GET /api/v1/model/status`

## Project Structure

```text
Handwritten-Maths-Formula/
|-- README.md
|-- .dockerignore
|-- .gitignore
|-- docker-compose.yml
|-- docker-compose.override.yml
|-- db/
|   `-- init.sql
|-- ml_models/
|   `-- yolo/
|       |-- best.pt
|       `-- config.yaml
|-- backend/
|   |-- Dockerfile
|   |-- requirements.txt
|   |-- pyproject.toml
|   |-- alembic.ini
|   |-- conftest.py
|   |-- sitecustomize.py
|   |-- test.db
|   |-- alembic/
|   |   |-- env.py
|   |   |-- script.py.mako
|   |   `-- versions/
|   |       `-- 20260611_0001_create_equation_history.py
|   `-- app/
|       |-- main.py
|       |-- api/
|       |   |-- deps.py
|       |   `-- v1/
|       |       `-- endpoints/
|       |           |-- auth.py
|       |           |-- expression.py
|       |           |-- history.py
|       |           |-- model.py
|       |           `-- predict.py
|       |-- core/
|       |   |-- config.py
|       |   |-- database.py
|       |   `-- security.py
|       |-- crud/
|       |   |-- crud_expression.py
|       |   `-- crud_history.py
|       |-- db/
|       |   |-- base.py
|       |   `-- models.py
|       |-- models/
|       |   |-- expression.py
|       |   |-- history.py
|       |   `-- user.py
|       |-- schemas/
|       |   |-- expression.py
|       |   |-- history.py
|       |   |-- prediction.py
|       |   |-- token.py
|       |   `-- user.py
|       |-- services/
|       |   |-- expression_parser.py
|       |   |-- expression_service.py
|       |   |-- image_preprocessing.py
|       |   |-- latex_generator.py
|       |   |-- pix2tex_service.py
|       |   |-- predict_service.py
|       |   |-- symbol_detection.py
|       |   `-- yolo_service.py
|       |-- utils/
|       |   |-- image_processing.py
|       |   `-- latex_parser.py
|       `-- tests/
|           |-- conftest.py
|           |-- test_api.py
|           |-- test_database_config.py
|           |-- test_expression_parser.py
|           |-- test_image_preprocessing.py
|           |-- test_latex_generator.py
|           |-- test_services.py
|           `-- test_symbol_detection.py
`-- frontend/
    |-- Dockerfile
    |-- index.html
    |-- nginx.conf
    |-- package.json
    |-- package-lock.json
    |-- vite.config.js
    `-- src/
        |-- App.jsx
        |-- index.css
        |-- main.jsx
        |-- components/
        |   |-- Results/
        |   |   `-- PredictionResult.jsx
        |   |-- Upload/
        |   |   `-- ImageUploader.jsx
        |   |-- canvas/
        |   |   `-- Canvas.jsx
        |   `-- common/
        |       |-- ErrorBoundary.jsx
        |       |-- Header.jsx
        |       |-- Sidebar.jsx
        |       `-- Skeleton.jsx
        |-- context/
        |   |-- AuthContext.jsx
        |   `-- ToastContext.jsx
        |-- hooks/
        |   `-- useCanvas.js
        |-- pages/
        |   |-- About.jsx
        |   |-- Dashboard.jsx
        |   |-- History.jsx
        |   |-- Home.jsx
        |   |-- Login.jsx
        |   `-- Register.jsx
        `-- services/
            `-- api.js
```

## Requirements

For Docker-based development:

- Docker
- Docker Compose
- Enough disk space for Python packages, Node packages, PostgreSQL data, and Pix2Tex/Hugging Face model cache

For local development without Docker:

- Python 3.12
- Node.js 20 or newer
- npm
- PostgreSQL 15 or compatible PostgreSQL server

## Quick Start with Docker

From the repository root:

```bash
docker compose up --build
```

Services:

| Service | URL / Port | Description |
| --- | --- | --- |
| Frontend | `http://localhost` | Nginx-served React build |
| Backend | `http://localhost:8000` | FastAPI API |
| API docs | `http://localhost:8000/docs` | Swagger UI |
| OpenAPI JSON | `http://localhost:8000/api/v1/openapi.json` | OpenAPI schema |
| PostgreSQL | `localhost:5432` | Database exposed from the `db` container |

Useful Docker commands:

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
docker compose down
```

To remove persisted database, upload, and model-cache volumes:

```bash
docker compose down -v
```

Only run the volume removal command when you intentionally want to delete persisted local data.

## Local Development

### Backend

Create and activate a virtual environment from `backend/`:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Set a database URL or provide the individual database settings described below. Then run:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend reads environment variables from:

- `.env`
- `.env.local`
- `.env.development`

### Frontend

Install dependencies from `frontend/`:

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server runs on:

```text
http://localhost:5173
```

During development, `frontend/vite.config.js` proxies `/api` requests to:

```text
http://localhost:8000
```

## Environment Variables

Backend configuration is defined in `backend/app/core/config.py`.

| Variable | Default | Description |
| --- | --- | --- |
| `API_V1_STR` | `/api/v1` | Prefix for versioned API routes |
| `PROJECT_NAME` | `Handwritten Mathematical Expression Recognition` | FastAPI application title |
| `BACKEND_CORS_ORIGINS` | `http://localhost,http://localhost:3000,http://localhost:5173` | Allowed frontend origins, comma-separated or JSON list |
| `DATABASE_URL` | unset | Full SQLAlchemy database URL; overrides individual database settings |
| `DATABASE_DRIVER` | `postgresql+psycopg2` | SQLAlchemy database driver |
| `DATABASE_HOST` | `localhost` | Database host outside Docker |
| `DATABASE_PORT` | `5432` | Database port |
| `DATABASE_NAME` | `hmer` | Database name |
| `DATABASE_USER` | `postgres` | Database user |
| `DATABASE_PASSWORD` | `postgres` | Database password |
| `APP_RUNTIME` | `local` | Set to `docker`, `compose`, or `container` to resolve the database host as `db` |
| `PIX2TEX_CACHE_DIR` | `/app/.cache/pix2tex` | Pix2Tex cache location |
| `YOLO_MODEL_PATH` | `ml_models/yolo/best.pt` | Legacy YOLO model path |
| `ENVIRONMENT` | `development` | Runtime environment label returned by health checks |
| `DEBUG` | `false` | Enables debug logging when truthy |
| `HF_HOME` | set in Docker | Hugging Face model cache path |
| `XDG_CACHE_HOME` | set in Docker | General cache path |

Docker Compose also supports:

| Variable | Default | Description |
| --- | --- | --- |
| `POSTGRES_USER` | `postgres` | PostgreSQL user for the database container |
| `POSTGRES_PASSWORD` | `postgres` | PostgreSQL password for the database container |
| `POSTGRES_DB` | `hmer` | PostgreSQL database name |

Example backend `.env.local`:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/hmer
BACKEND_CORS_ORIGINS=http://localhost,http://localhost:5173
ENVIRONMENT=development
DEBUG=true
```

## API Reference

### Health

```http
GET /
GET /health
```

`GET /health` returns database status, model status, and environment metadata.

### Prediction

```http
POST /api/v1/predict
```

Request:

- Multipart form data
- Field name: `image`
- Supported image intent: handwritten mathematical expression image
- Endpoint description indicates JPG, PNG, and WEBP uploads

Example:

```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -F "image=@sample-expression.png"
```

Response includes:

- Generated LaTeX
- Saved image path
- Prediction/history id
- UTC timestamp
- Total processing time
- Preprocessing time
- OCR time
- Confidence value
- Confidence source

Pix2Tex does not currently expose calibrated confidence. Successful non-empty OCR responses use a documented placeholder confidence of `0.80` with:

```text
confidence_source=placeholder_success_default
```

### Expression Recognition Alias

```http
POST /api/v1/expressions/recognize
```

This endpoint uses the same `PredictService` path as `/api/v1/predict`.

### History

```http
GET /api/v1/history
DELETE /api/v1/history/{history_id}
```

`GET /api/v1/history` query parameters:

| Parameter | Default | Description |
| --- | --- | --- |
| `search` | empty string | Search text, max 200 characters |
| `page` | `1` | Page number, minimum 1 |
| `page_size` | `10` | Items per page, minimum 1 and maximum 50 |

Example:

```bash
curl "http://localhost:8000/api/v1/history?page=1&page_size=10&search=sum"
```

### Model Status

```http
GET /api/v1/model/status
```

Returns the Pix2Tex service health state.

### Auth

```http
POST /api/v1/auth/login
```

The current login endpoint is a placeholder and returns a mock bearer token.

## Frontend Routes

| Route | Purpose |
| --- | --- |
| `/` | Main upload/drawing and prediction experience |
| `/history` | Prediction history |
| `/about` | Project/about page |
| `/login` | Login page |
| `/register` | Registration page |

Unknown routes redirect to `/`.

## Model Lifecycle

Pix2Tex is loaded once during FastAPI startup through `app.services.pix2tex_service.Pix2TexOCRService`.

Startup fails fast if the model cannot load. A singleton instance is reused for every request, and inference is protected by a lock for thread-safe access.

Health is available at:

- `GET /health`
- `GET /api/v1/model/status`

Containers persist Pix2Tex/Hugging Face cache data in the `pix2tex_cache` Docker volume to avoid repeated downloads after initial setup. Uploaded images are persisted in `backend_uploads`.

## Preprocessing Policy

Pix2Tex receives a PIL image, not the previous YOLO tensor format.

The active OCR preprocessing keeps:

- Grayscale conversion, because math meaning is stroke intensity rather than color.
- Light median denoising, because it removes isolated specks while preserving edges.
- Autocontrast, because it improves faint handwriting without hard binarization.

The active OCR path skips:

- Adaptive thresholding
- Fixed `640x640` padding
- YOLO-style float normalization

Those steps were YOLO-oriented and can degrade thin bars, dots, roots, brackets, and matrix layouts.

## Database and Migrations

The Docker stack runs PostgreSQL 15 Alpine with:

- Database: `hmer`
- User: `postgres`
- Password: `postgres`
- Host from backend container: `db`
- Host from local machine: `localhost`
- Port: `5432`

The project includes Alembic configuration in `backend/alembic.ini` and migration files in `backend/alembic/versions/`.

The current migration creates equation history storage:

```text
backend/alembic/versions/20260611_0001_create_equation_history.py
```

## Testing

Backend pytest configuration lives in `backend/pyproject.toml`.

Run backend tests from `backend/`:

```bash
pytest
```

Or from the repository root:

```bash
pytest backend/app/tests
```

Frontend build check:

```bash
cd frontend
npm run build
```

Automated backend tests cover:

- Startup and API health behavior
- Database configuration
- Pix2Tex service reuse and prediction flow
- Upload validation and response shape
- History-compatible persistence
- Image preprocessing
- Legacy expression parser and LaTeX generator utilities
- Legacy symbol detection utilities

## Troubleshooting

### First Docker startup is slow

Pix2Tex and Hugging Face model assets may need to download and initialize. After the first successful startup, Docker keeps these files in the `pix2tex_cache` volume.

### Backend reports unhealthy model status

Check backend logs:

```bash
docker compose logs -f backend
```

Common causes include missing model cache files, failed model download, insufficient disk space, or dependency issues.

### Frontend cannot reach the backend locally

Confirm the backend is running:

```bash
curl http://localhost:8000/health
```

For Vite development, requests to `/api` are proxied to `http://localhost:8000`.

### Database connection fails

For Docker, confirm the database container is healthy:

```bash
docker compose ps
docker compose logs -f db
```

For local development, set `DATABASE_URL` or verify `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`, `DATABASE_USER`, and `DATABASE_PASSWORD`.

### Prediction succeeds but confidence is always similar

This is expected with the current Pix2Tex integration. Pix2Tex does not expose calibrated confidence through this service, so the backend returns a placeholder confidence for successful non-empty OCR output.

## Validation Notes

Automated tests verify the service contract and key processing paths, but recognition quality should still be validated with real handwritten samples before production release.

Recommended manual validation set:

- Fractions
- Square roots and nth roots
- Integrals
- Summations
- Products
- Matrices
- Greek symbols
- Superscripts and subscripts
- Multi-line expressions
- Faint handwriting
- Dense expressions with small symbols

## Current Limitations

- Authentication is currently represented by a placeholder login endpoint.
- Pix2Tex confidence is not calibrated in the API response.
- YOLO-based symbol detection files are retained but are not the production prediction path.
- Recognition quality depends heavily on image clarity, expression layout, and Pix2Tex model behavior.
