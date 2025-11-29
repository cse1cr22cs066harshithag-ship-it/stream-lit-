# Streamlit CloudHealthCare Deployment Guide

## Quick Start (Local Testing)

### 1. Create Virtual Environment (if not already done)

```powershell
cd D:\project\CloudHealthCare
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Streamlit Requirements

```powershell
pip install -r requirements_streamlit.txt
```

### 3. Run the Streamlit App Locally

```powershell
streamlit run app.py
```

Your app will open at `http://localhost:8501` in your browser.

### 4. Test Locally

- Register a patient account (e.g., username: `patient1`, password: `test123`, usertype: `Patient`)
- Register a doctor account (e.g., username: `doctor1`, password: `test123`, usertype: `Doctor`)
- Login as patient and upload symptoms
- Login as doctor to view all patient data

---

## Deploy to Streamlit Cloud (Free & Easy)

### Prerequisites

- Your repo pushed to GitHub on branch `main` (with `app.py`, `streamlit_db.py`, `requirements_streamlit.txt`)
- GitHub account

### Step 1: Commit and Push to GitHub

```powershell
git add app.py streamlit_db.py requirements_streamlit.txt
git commit -m "Add Streamlit version of CloudHealthCare"
git push origin main
```

### Step 2: Create Streamlit Cloud Account

- Visit https://streamlit.io/cloud
- Click "Sign up" → Create a Streamlit account (use GitHub login for simplicity)

### Step 3: Deploy Your App

- In Streamlit Cloud dashboard, click "New app"
- Select your GitHub repo (`cse1cr22cs066harshithag-ship-it/major-project-`)
- Select branch: `main`
- Set Main file path: `app.py` (or `CloudHealthCare/app.py` if the repo structure requires it)
- Click "Deploy"

Streamlit Cloud will:

- Clone your repo
- Install packages from `requirements_streamlit.txt`
- Run `streamlit run app.py`
- Provide a public URL like `https://your-username-cloudhealthcare.streamlit.app`

### Step 4: Share Your App

Your app is now live and publicly accessible. Share the URL with anyone!

---

## Key Differences from Django Version

| Feature            | Django                              | Streamlit                                   |
| ------------------ | ----------------------------------- | ------------------------------------------- |
| Database           | SQLite (local) or Postgres (Render) | SQLite (Streamlit Cloud)                    |
| Deployment         | Render (complex, build failures)    | Streamlit Cloud (1-click deploy)            |
| Session Management | Django sessions (DB-backed)         | Streamlit session state (in-memory)         |
| Authentication     | Database queries                    | Simple plaintext comparison (upgrade later) |
| Scaling            | Limited on free tier                | Built-in auto-scaling                       |
| Cost               | Render free tier limited            | Free tier very generous                     |

---

## Features Included

✅ **User Registration**

- Patient and Doctor user types
- SQLite database storage
- Duplicate username check

✅ **Patient Features**

- Login with credentials
- Upload heart disease symptoms (13 parameters)
- Automatic encryption/encoding of data
- AI-based health predictions (Normal/Abnormal)
- View personal prediction history
- Logout

✅ **Doctor Features**

- Login with credentials
- View all patient data (encrypted symptoms + predictions)
- Sorted by date
- Logout

✅ **ML & Encryption**

- Lazy-loads RandomForestClassifier with sklearn
- Optional homomorphic encryption (falls back to base64 if unavailable)
- Graceful error handling

✅ **Database**

- SQLite (works everywhere, no setup needed)
- User table with unique username constraint
- Patient data with ForeignKey to user
- Full audit trail with timestamps

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'streamlit'`

**Solution:** Install requirements:

```powershell
pip install -r requirements_streamlit.txt
```

### Issue: App shows "Prediction unavailable (fallback mode)"

**Reason:** ML dependencies missing or dataset not found.
**Solution:**

- Ensure `requirements_streamlit.txt` has numpy, pandas, scikit-learn.
- Check that `Dataset/heart.csv` exists in your repo.
- Both are included in the commit, so Streamlit Cloud should have them.

### Issue: Streamlit Cloud shows "Build failed"

**Solution:**

- Check the build logs in Streamlit Cloud console.
- Ensure `requirements_streamlit.txt` only lists valid PyPI package names.
- Verify your repo has all required files: `app.py`, `streamlit_db.py`, `requirements_streamlit.txt`.

### Issue: Database persists but I want to reset it

**Solution:** Delete the `cloudhealthcare.db` file locally, or reset Streamlit Cloud cache:

- In Streamlit Cloud app settings, click "Advanced settings" → "Clear cache"

---

## Optional: Upgrade Authentication (Security)

For production, consider:

- Using `streamlit-authenticator` for better password hashing
- Adding email verification on signup
- Using environment variables for sensitive config

Example:

```bash
pip install streamlit-authenticator
```

Then import and use in `app.py` for secure auth.

---

## Optional: Add PostgreSQL for Production Scale

If you need persistent data across multiple deployments:

1. Create a PostgreSQL database on a free provider (e.g., Railway.app, Render)
2. Update `streamlit_db.py` to use `psycopg2` instead of `sqlite3`
3. Set `DATABASE_URL` as a secret in Streamlit Cloud settings
4. Redeploy

---

## File Structure

```
CloudHealthCare/
├── app.py                    # Main Streamlit app
├── streamlit_db.py          # Database utilities
├── requirements_streamlit.txt # Streamlit dependencies
├── Dataset/
│   └── heart.csv           # ML training data
├── Homomorphic.py          # (Optional) Encryption utilities
└── STREAMLIT_DEPLOY.md     # This file
```

---

## Next Steps

1. ✅ Test locally: `streamlit run app.py`
2. ✅ Commit and push to GitHub
3. ✅ Deploy to Streamlit Cloud
4. ✅ Share the public URL with users/reviewers

**Expected deployment time:** 2-5 minutes on Streamlit Cloud.

Enjoy your live app! 🚀
