# CloudHealthCare — Postgres + Render deployment

This repository contains a Django app (`CloudApp`) and models adapted to use a Postgres database. The files added explain how to create the database, install dependencies, and deploy to Render.

Quick tasks performed
- Updated `CloudApp/models.py` to use a proper `ForeignKey` and Postgres-friendly fields.
- Added `db.txt` with Postgres DDL to create the required tables.
- Added `requirements.txt` and `Procfile` for Render deployment.

Local testing (Windows PowerShell)

1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Configure the database locally (example using a local Postgres):

Set the `DATABASE_URL` environment variable in PowerShell, e.g.:

```powershell
$env:DATABASE_URL = "postgres://user:password@localhost:5432/cloudhealth"
```

Or place the variable in a `.env` file and use `python-dotenv`/`dj-database-url` in `settings.py`.

3. Run migrations and start the dev server:

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Deploying to Render (high-level)

1. Push this repo to GitHub.
2. In Render, create a new Web Service and connect to the GitHub repo.
3. Set build command: `pip install -r requirements.txt`
4. Set start command (Procfile is picked up automatically) or set env var `WSGI_MODULE` to your project's WSGI module, e.g. `myproject.wsgi`.
5. Create a managed Postgres database in Render (Database → New Database). After it's created, copy the `DATABASE_URL` connection string from Render and add it to the Web Service's environment variables.
6. Set `PORT` environment variable if needed and any secret keys (`DJANGO_SECRET_KEY`, etc.).
7. Deploy; Render will build and start the service.

Notes & next steps
- I couldn't find `settings.py` or `manage.py` in the workspace; if your Django project uses a different layout, update `WSGI_MODULE` and `manage.py` path accordingly.
- I recommend switching to Django's built-in `auth.User` for password handling and using `django-environ` or `dj-database-url` in `settings.py` to read `DATABASE_URL`.
- If you want, I can:
  - update `settings.py` to use `dj-database-url` and environment variables,
  - add a `render.yaml` for full Render infra-as-code,
  - or prepare a Dockerfile for containerized deployment.