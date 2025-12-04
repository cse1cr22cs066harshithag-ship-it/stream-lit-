# CloudHealthCare Project Setup Guide

This guide provides step-by-step instructions to set up and run the CloudHealthCare project locally.

## Prerequisites

- **Python 3.11.2** installed (download from https://www.python.org/downloads/)
- **Git** installed (optional, for version control)
- **Windows PowerShell** or Command Prompt

## Step 1: Navigate to Project Directory

```powershell
cd D:\project\CloudHealthCare
```

## Step 2: Create a Virtual Environment

Use Python's built-in `venv` module to create an isolated Python environment:

```powershell
python -m venv venv
```

This creates a `venv` folder with a fresh Python installation isolated from your system Python.

## Step 3: Activate the Virtual Environment

On **Windows PowerShell**:

```powershell
.\venv\Scripts\Activate.ps1
```

On **Windows Command Prompt (cmd)**:

```cmd
venv\Scripts\activate.bat
```

**Note:** After activation, your prompt should show `(venv)` at the beginning, like:

```
(venv) PS D:\project\CloudHealthCare>
```

## Step 4: Upgrade pip, setuptools, and wheel

```powershell
python -m pip install --upgrade pip setuptools wheel
```

## Step 5: Install Project Dependencies

Install all required packages from `requirements.txt`:

```powershell
pip install -r requirements.txt
```

This will install:

- Django 4.2.26
- psycopg2-binary (PostgreSQL adapter)
- dj-database-url (database URL parsing)
- gunicorn (production WSGI server)
- whitenoise (static file serving)
- python-dotenv (environment variable management)
- django-extensions (optional developer utilities)
- And any ML dependencies you've uncommented

**Installation time:** 2-5 minutes depending on your internet speed and whether you've uncommented ML packages.

## Step 6: Run Database Migrations

Create the local SQLite database schema:

```powershell
python manage.py makemigrations
```

Apply migrations to the database:

```powershell
python manage.py migrate
```

## Step 7: Run the Development Server

Start the Django development server:

```powershell
python manage.py runserver
```

**Expected output:**

```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

## Step 8: Access the Application

Open your web browser and visit:

```
http://127.0.0.1:8000/
```

You should see the CloudHealthCare home page.

## Testing the Full Application Flow

### 1. Register a Patient Account

1. Click **Register** on the home page
2. Fill in:
   - Username: `patient1`
   - Password: `password123`
   - Contact: `9876543210`
   - Email: `patient@example.com`
   - Address: `123 Main St, City`
   - Description: `Patient Test`
   - User Type: **Patient** (select from dropdown)
3. Click **Submit**
4. Confirm success message appears

### 2. Register a Doctor Account

1. Click **Register** again
2. Fill in:
   - Username: `doctor1`
   - Password: `password123`
   - Contact: `9876543211`
   - Email: `doctor@example.com`
   - Address: `Hospital, City`
   - Description: `Doctor Test`
   - User Type: **Doctor** (select from dropdown)
3. Click **Submit**

### 3. Patient Login and Upload Symptoms

1. Click **Patient Login**
2. Enter credentials:
   - Username: `patient1`
   - Password: `password123`
3. Click **Login**
4. You should see the **Patient Screen** with navigation menu
5. Click **Upload Encrypted Symptoms to Cloud**
6. Fill in the symptom form:
   - Age: 50
   - Gender: Male
   - CP: 3
   - Blood Pressure: 120
   - Cholesterol Level: 200
   - FBS: 120
   - Rest ECG: 1
   - Thalach: 100
   - Exang: 0
   - Old Peak: 2.5
   - Slope: 1
   - CA: 0
   - Thal: 2
7. Click **Submit**
8. You should see:
   - Success message at the top
   - Encrypted data preview
   - Predicted health status (Normal or Abnormal, or "Prediction unavailable" if ML deps aren't installed)

### 4. View Predictions

1. While logged in as patient, click **View Predictions**
2. You should see a table with all your submitted patient data records

### 5. Doctor Login and View Patient Data

1. Click **Logout** to end patient session
2. Click **Doctor Login**
3. Enter credentials:
   - Username: `doctor1`
   - Password: `password123`
4. Click **Login**
5. You should see the **Doctor Screen**
6. Click **Get Patient Data from Cloud**
7. You should see a table with all patient data from all patients in the system

## Useful Management Commands

### Create a Superuser (Admin Account)

```powershell
python manage.py createsuperuser
```

Follow the prompts to create an admin account, then visit `http://127.0.0.1:8000/admin/` to access Django admin.

### Run Django Shell (Interactive Python Console)

```powershell
python manage.py shell
```

Useful commands once in the shell:

```python
from CloudApp.models import UserSignup, PatientData

# List all users
UserSignup.objects.all()

# List all patient data
PatientData.objects.all()

# Count records
PatientData.objects.count()

# Get patient data for a specific user
PatientData.objects.filter(user__username='patient1')
```

### Check for Django Errors

```powershell
python manage.py check
```

### Collect Static Files (For Production)

```powershell
python manage.py collectstatic --noinput
```

## Optional: Install ML Dependencies

If you want to enable encryption and ML-based predictions (instead of the fallback mode), uncomment the ML packages in `requirements.txt` and install them:

```powershell
# Edit requirements.txt and uncomment the ML dependency lines, then:
pip install -r requirements.txt
```

ML packages include: numpy, pandas, scikit-learn, etc.

**Note:** ML packages add 200+ MB to your installation and may take 5-10 minutes to install on first run.

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'django'"

**Solution:** Ensure the virtual environment is activated:

```powershell
.\venv\Scripts\Activate.ps1
```

### Issue: "python: command not found"

**Solution:** Make sure Python 3.11.2 is installed and in your PATH. Test with:

```powershell
python --version
```

### Issue: Port 8000 already in use

**Solution:** Run the server on a different port:

```powershell
python manage.py runserver 8001
```

Then visit `http://127.0.0.1:8001/`

### Issue: "No migrations to apply"

**Solution:** Ensure migrations are created and applied:

```powershell
python manage.py makemigrations CloudApp
python manage.py migrate
```

### Issue: Database lock error or "table does not exist"

**Solution:** Remove the old database and recreate it:

```powershell
Remove-Item db.sqlite3 -Force
python manage.py migrate
```

## Deactivating the Virtual Environment

When you're done, exit the virtual environment by typing:

```powershell
deactivate
```

Your prompt will return to normal (without the `(venv)` prefix).

## Production Deployment (Render)

See the project's **README.md** or deployment documentation for steps to deploy to Render with PostgreSQL.

## Summary of Key Files

- `manage.py` — Django management script
- `requirements.txt` — Python package dependencies
- `Cloud/settings.py` — Django configuration
- `Cloud/urls.py` — URL routing for the project
- `CloudApp/views.py` — Application views (login, upload, prediction, etc.)
- `CloudApp/models.py` — Database models (UserSignup, PatientData)
- `CloudApp/urls.py` — URL routing for the CloudApp
- `CloudApp/templates/` — HTML templates for the UI

## Support

If you encounter issues:

1. Check the server console output for error messages.
2. Run `python manage.py check` to validate Django setup.
3. Run `python manage.py shell` and test imports manually.
4. Ensure all files in `requirements.txt` are installed with `pip list`.

Good luck! 🏥
