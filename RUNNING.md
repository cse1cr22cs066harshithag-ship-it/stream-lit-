# CloudHealthCare — Running the Demo

This guide walks you through setting up and launching the CloudHealthCare Streamlit application locally.

## Prerequisites

- **Python 3.9+** (check with `python --version`)
- **Windows PowerShell** or **Command Prompt**
- Internet connection (to download Python packages)

---

## Quick Start (Copy & Paste Commands)

### 1. Open PowerShell and navigate to the project

```powershell
cd D:\project\CloudHealthCare
```

### 2. Allow script execution (one-time, for this session)

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### 3. Create and activate virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

After activation, your prompt will show `(.venv)` at the start.

### 4. Upgrade pip and install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

This installs: `streamlit`, `pandas`, `numpy`, `scikit-learn`, `python-dotenv`, and other required packages.

### 5. Run preflight check (optional but recommended)

```powershell
python preflight_check.py
```

Expected output:

```
CloudHealthCare preflight check
Python: 3.x.x ...
OK: streamlit (version: ...)
OK: pandas (version: ...)
OK: numpy (version: ...)
OK: sklearn (version: ...)
OK: Homomorphic module imported
Initialized database (init_db() called)
Database tables:
 - user_signup
```
