"""
Preflight health check for CloudHealthCare project.
Run this after activating your virtualenv and installing requirements:

    python preflight_check.py

It will check for key Python packages, initialize the DB, and list DB tables.
"""
import importlib
import sqlite3
import sys
from pathlib import Path

REQS = [
    'streamlit',
    'pandas',
    'numpy',
    'sklearn',
]

print('CloudHealthCare preflight check')
print('Python:', sys.version.splitlines()[0])
print()

# Check packages
for pkg in REQS:
    try:
        mod = importlib.import_module(pkg)
        print(f'OK: {pkg} (version: {getattr(mod, "__version__", "unknown")})')
    except Exception as e:
        print(f'MISSING: {pkg} -> {e}')

# Check Homomorphic module availability
try:
    import Homomorphic
    print('OK: Homomorphic module imported')
except Exception as e:
    print('Homomorphic import error:', e)

# Initialize DB and list tables
DB = 'cloudhealthcare.db'
if not Path(DB).exists():
    print('\nDB file does not exist yet; init_db will create it.')

try:
    from streamlit_db import init_db
    init_db()
    print('Initialized database (init_db() called)')
except Exception as e:
    print('Error initializing DB:', e)

try:
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print('Database tables:')
    for t in tables:
        print(' -', t)
    conn.close()
except Exception as e:
    print('Error reading DB:', e)

print('\nPreflight check complete. If any "MISSING" items appeared, install them with:')
print('  pip install -r requirements.txt')
print('\nTo run the app:')
print('  python -m streamlit run app.py')
