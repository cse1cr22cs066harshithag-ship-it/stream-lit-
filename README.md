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

Deploying to Streamlit Cloud (recommended)

1. Commit these Streamlit files to GitHub: `app.py`, `streamlit_db.py`, `requirements_streamlit.txt`.
2. Push the repo to GitHub (branch `main`).
3. Go to https://streamlit.io/cloud and sign in with your GitHub account.
4. Click "New app", select this repository and branch `main`, set the main file to `app.py`, then click "Deploy".
5. Streamlit Cloud will install packages from `requirements_streamlit.txt` and launch the app. The public URL will be provided by Streamlit Cloud.

Notes & next steps

- The Streamlit app uses an embedded SQLite DB: `cloudhealthcare.db` in the repo root. This file is ignored by `.gitignore` so it won't be pushed to GitHub; Streamlit Cloud stores app data separately.
- If you want persistence across deployments, configure an external Postgres DB and update `streamlit_db.py` to use `DATABASE_URL`.
- If you prefer to keep the Django version, I left the Django files in the repo; but Streamlit is simpler to deploy and maintain on Streamlit Cloud.

If you'd like, I can:

- create a Git commit in this workspace with the Streamlit files staged (you'll still need to push), or
- update `streamlit_db.py` to support `DATABASE_URL` for external DBs, or
- add a small `start_streamlit.ps1` script to make local testing one-line.
