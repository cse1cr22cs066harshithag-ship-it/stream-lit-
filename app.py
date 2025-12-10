"""
CloudHealthCare Streamlit Application
Patient registration, login, symptom upload, prediction, and doctor view.
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import base64
import os

# Import database utilities
from streamlit_db import (
    init_db,
    register_user,
    login_user,
    save_patient_data,
    get_user_predictions,
    get_all_patient_data,
    get_user_by_id,
    get_user_by_username,
    calculate_trend_difference,
    calculate_encrypted_statistics,
    calculate_granular_risk_score,
    save_risk_score,
    get_risk_scores,
    grant_access,
    revoke_access,
    get_authorized_patients,
    get_all_doctors
)
from streamlit_db import save_appointment, get_user_appointments
from streamlit_db import (
    save_medication,
    get_user_medications,
    mark_medication_taken,
    request_refill
)
from ui_helpers import inject_style, status_badge, metric_card

# Initialize database
init_db()

# Page config
st.set_page_config(page_title="CloudHealthCare", layout="wide", initial_sidebar_state="expanded")

# Custom CSS
st.markdown("""
<style>
    .main { padding: 2rem; }
    .header { text-align: center; color: #c41e3a; }
    .success { color: green; font-weight: bold; }
    .error { color: red; font-weight: bold; }
    .stMetric { background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# ==================== ML Model Loader ====================
_ml_model = None
_ml_initialized = False

def load_ml_model():
    """Lazy load ML model for predictions."""
    global _ml_model, _ml_initialized
    if _ml_initialized:
        return _ml_model
    _ml_initialized = True
    
    try:
        from sklearn.ensemble import RandomForestClassifier
        from Homomorphic import encryptData
        
        # Try to load dataset and train model
        dataset_path = os.path.join(os.path.dirname(__file__), "Dataset", "heart.csv")
        if not os.path.exists(dataset_path):
            st.warning(f"Dataset not found at {dataset_path}. Using fallback predictions.")
            return None
        
        df = pd.read_csv(dataset_path)
        data = df.values
        X = data[:, 0:data.shape[1] - 1]
        Y = data[:, data.shape[1] - 1]
        
        # Try encryption
        try:
            homo_X = encryptData(X)
        except Exception as e:
            st.warning(f"Encryption failed: {e}. Using plaintext training.")
            homo_X = X
        
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(homo_X, Y, test_size=0.2, random_state=42)
        
        rf = RandomForestClassifier(random_state=42, n_jobs=-1)
        rf.fit(X_train, y_train)
        _ml_model = (rf, encryptData)
        return _ml_model
    except Exception as e:
        st.warning(f"ML model initialization failed: {e}. Predictions will use fallback method.")
        return None

# ==================== Helper Functions ====================
def make_prediction(symptoms: list) -> str:
    """Make prediction based on symptoms."""
    try:
        model = load_ml_model()
        if model is None:
            return "Prediction unavailable (fallback mode)"
        
        rf, encrypt_func = model
        try:
            data = np.asarray([symptoms])
            enc_data = encrypt_func(data)
            predict = rf.predict(enc_data)
            result = "Abnormal" if int(predict[0]) == 1 else "Normal"
            return result
        except Exception as e:
            return f"Prediction failed: {str(e)[:50]}"
    except Exception as e:
        return "Prediction unavailable"

def encrypt_symptoms(symptoms: list) -> str:
    """Encrypt or encode symptoms."""
    try:
        from Homomorphic import encryptData
        data = np.asarray([symptoms])
        enc_data = encryptData(data)
        return str(enc_data[0])[:100]  # Display first 100 chars
    except:
        # Fallback: base64 encode
        plaintext = " ".join(str(s) for s in symptoms)
        return base64.b64encode(plaintext.encode()).decode()[:100]

# ==================== Pages ====================

def page_home():
    """Home page with options."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 class='header'>🏥 CloudHealthCare</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Homomorphic Encryption for Patient Data</h3>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📋 Register")
        if st.button("Go to Register", key="home_register"):
            st.session_state.page = 'register'
            st.rerun()
    
    with col2:
        st.subheader("👤 Patient Login")
        if st.button("Go to Patient Login", key="home_patient_login"):
            st.session_state.page = 'patient_login'
            st.rerun()
    
    with col3:
        st.subheader("👨‍⚕️ Doctor Login")
        if st.button("Go to Doctor Login", key="home_doctor_login"):
            st.session_state.page = 'doctor_login'
            st.rerun()
    
    st.markdown("---")
    st.info("📌 **Features:**\n- Secure patient registration\n- Symptom upload with encryption\n- AI-based health predictions\n- Doctor access to all patient data")

def page_register():
    """Registration page."""
    st.title("📋 Register")
    
    with st.form("register_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email")
        address = st.text_area("Address", height=80)
        description = st.text_area("Description (optional)", height=80)
        usertype = st.selectbox("User Type", ["Patient", "Doctor"])
        
        if st.form_submit_button("Register"):
            if not username or not password:
                st.error("Username and password are required")
            else:
                success, msg = register_user(username, password, phone, email, address, description, usertype)
                if success:
                    st.success(msg)
                    st.session_state.page = 'home'
                    st.rerun()
                else:
                    st.error(msg)
    
    if st.button("← Back to Home"):
        st.session_state.page = 'home'
        st.rerun()

def page_patient_login():
    """Patient login page."""
    st.title("👤 Patient Login")
    
    with st.form("patient_login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Login"):
            success, user = login_user(username, password, "Patient")
            if success:
                st.session_state.user = user
                st.session_state.page = 'patient_dashboard'
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    if st.button("← Back to Home"):
        st.session_state.page = 'home'
        st.rerun()

def page_doctor_login():
    """Doctor login page."""
    st.title("👨‍⚕️ Doctor Login")
    
    with st.form("doctor_login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Login"):
            success, user = login_user(username, password, "Doctor")
            if success:
                st.session_state.user = user
                st.session_state.page = 'doctor_dashboard'
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    if st.button("← Back to Home"):
        st.session_state.page = 'home'
        st.rerun()

def page_patient_dashboard():
    """Patient dashboard."""
    if not st.session_state.user:
        st.session_state.page = 'home'
        st.rerun()
    
    user = st.session_state.user
    inject_style()
    st.title(f"👤 Patient Dashboard - {user['username']}")

    # Greeting and status
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"<div class='ch-header'>Hi, {user['username'].title()} 👋</div>", unsafe_allow_html=True)
        st.markdown("<div class='small-muted'>Welcome back — here's your health snapshot for today.</div>", unsafe_allow_html=True)
    with col2:
        status_badge("Stable")

    st.markdown("---")

    # Next Action Card + Vitals
    na_col, vit_col = st.columns([2, 3])
    with na_col:
        st.markdown("<div class='ch-card'>", unsafe_allow_html=True)
        st.markdown("<div style='font-weight:700;font-size:18px'>Next Action</div>")
        st.markdown("<div style='margin-top:8px'>No upcoming appointments. Book a check-in if you feel unwell.</div>")
        if st.button("Check-in Now"):
            st.info("Check-in flow not implemented in demo")
        st.markdown("</div>", unsafe_allow_html=True)

    with vit_col:
        st.markdown("<div class='ch-card'>", unsafe_allow_html=True)
        metric_cols = st.columns(3)
        with metric_cols[0]:
            metric_card("Blood Pressure", "120/78", trend="down", subtitle="Target: 120/80")
        with metric_cols[1]:
            metric_card("Steps Today", "6,204", trend="up", subtitle="Target: 8,000")
        with metric_cols[2]:
            metric_card("Sleep Score", "82", trend="up", subtitle="Last night")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Main Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Upload Symptoms", "My Records", "Appointments", "Medications"])

    with tab1:
        st.subheader("📤 Upload Encrypted Symptoms")
        with st.form("upload_symptoms_form"):
            age = st.number_input("Age", min_value=10, max_value=100, value=50)
            gender = st.selectbox("Gender", [0, 1], format_func=lambda x: "Female" if x == 0 else "Male")
            cp = st.number_input("Chest Pain Type (0-3)", min_value=0, max_value=3, value=0)
            trestbps = st.number_input("Resting Blood Pressure", min_value=80, max_value=200, value=120)
            chol = st.number_input("Cholesterol Level", min_value=100, max_value=400, value=200)
            fbs = st.selectbox("Fasting Blood Sugar > 120 mg/dl", [0, 1])
            restecg = st.number_input("Rest ECG (0-2)", min_value=0, max_value=2, value=0)
            thalach = st.number_input("Max Heart Rate", min_value=60, max_value=200, value=150)
            exang = st.selectbox("Exercise Induced Angina", [0, 1])
            oldpeak = st.number_input("Old Peak", min_value=0.0, max_value=10.0, value=1.0, step=0.1)
            slope = st.number_input("Slope (0-2)", min_value=0, max_value=2, value=1)
            ca = st.number_input("Number of Major Vessels (0-3)", min_value=0, max_value=3, value=0)
            thal = st.number_input("Thalassemia (0-3)", min_value=0, max_value=3, value=0)
            
            if st.form_submit_button("Submit"):
                symptoms = [age, gender, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]
                encrypted = encrypt_symptoms(symptoms)
                plaintext = " ".join(str(s) for s in symptoms)
                prediction = make_prediction(symptoms)
                patient_data = encrypted + "," + plaintext
                success, msg = save_patient_data(user['id'], patient_data, prediction, date.today())
                if success:
                    st.success(msg)
                    st.info(f"**Prediction: {prediction}**")
                else:
                    st.error(msg)

    with tab2:
        st.subheader("📊 My Records")
        predictions = get_user_predictions(user['id'])
        if predictions:
            df_data = []
            for p in predictions:
                enc_parts = p['patient_data'].split(",") if p['patient_data'] else ['', '']
                df_data.append({
                    'Date': p['predict_date'],
                    'Prediction': p['predict'],
                    'Encrypted': enc_parts[0][:50] + "..." if len(enc_parts[0]) > 50 else enc_parts[0],
                    'Symptoms': enc_parts[1] if len(enc_parts) > 1 else ''
                })
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            # Allow selecting a record to view detailed test results
            record_options = [f"{r['predict_date']} - {r['predict']}" for r in predictions]
            sel_idx = st.selectbox("Select a record to view details", options=["-- select --"] + record_options)
            if sel_idx != "-- select --":
                idx = record_options.index(sel_idx)
                record = predictions[idx]
                # Render Test Results Viewer (simplified lab view)
                st.markdown("---")
                st.header("Test Results")
                test_name = "Comprehensive Metabolic Panel"
                collected = record.get('predict_date', '')
                released = record.get('created_at', '')
                st.markdown(f"**{test_name}**  ")
                st.markdown(f"Collected: {collected}  ")
                st.markdown(f"Released: {released}  ")

                # Build some sample components using plaintext symptoms when available
                components = []
                symptoms_plain = ''
                try:
                    parts = record['patient_data'].split(',')
                    if len(parts) > 1:
                        symptoms_plain = parts[1]
                except Exception:
                    symptoms_plain = ''

                vals = {}
                try:
                    if symptoms_plain:
                        vals_list = [float(x) for x in symptoms_plain.split()]
                        age = int(vals_list[0]) if len(vals_list) > 0 else 50
                        chol = float(vals_list[4]) if len(vals_list) > 4 else 200.0
                    else:
                        age = 50
                        chol = 200.0
                except Exception:
                    age = 50
                    chol = 200.0

                # Simple deterministic calculations for demo
                hemoglobin = round(12.0 + (age - 50) * 0.02, 1)
                wbc = round(6.0 + (age - 50) * 0.01, 1)
                platelets = int(250 + (chol - 200) * 0.2)

                components.append(("Hemoglobin (g/dL)", hemoglobin, "13.5-17.5 (male) | 12.0-15.5 (female)"))
                components.append(("WBC (10^3/uL)", wbc, "4.0-11.0"))
                components.append(("Platelets (10^3/uL)", platelets, "150-450"))

                # Determine status
                abnormal_count = 0
                table_rows = []
                for name, value, ref in components:
                    status = 'Normal'
                    try:
                        if name.startswith('Hemoglobin'):
                            if value < 12.0:
                                status = 'Low'
                        if name.startswith('WBC'):
                            if value < 4.0 or value > 11.0:
                                status = 'Abnormal'
                        if name.startswith('Platelets'):
                            if value < 150 or value > 450:
                                status = 'Abnormal'
                    except Exception:
                        status = 'Unknown'
                    if status != 'Normal':
                        abnormal_count += 1
                    table_rows.append({'Component': name, 'Value': value, 'Reference': ref, 'Indicator': status})

                # Summary indicator
                if abnormal_count == 0:
                    st.success("All Results are within Normal Range")
                else:
                    st.warning(f"{abnormal_count} value(s) are outside the reference range")

                # Results table
                st.table(pd.DataFrame(table_rows))

                # Layman's explanation
                with st.expander("What Do These Results Mean?"):
                    if abnormal_count == 0:
                        st.write("Overall, your basic lab indicators are within expected ranges. Continue regular monitoring and follow your care plan.")
                    else:
                        st.write("Some values are outside typical ranges. This does not necessarily indicate a serious issue, but your care team will review these findings and advise next steps. If you feel unwell, message your care team.")

                # Next steps
                st.markdown("**Next Steps:**")
                st.write("Your doctor will review these results. If you have questions, contact your care team.")
                if st.button("Secure Message Care Team"):
                    st.info("Secure message sent (demo)")
        else:
            st.info("No records yet. Upload symptoms to begin.")

    with tab3:
        st.subheader("🗓️ Appointments")
        # 3-step scheduler: Step 1 - Select Reason/Provider, Step 2 - Select Date & Time, Step 3 - Confirm
        if 'appt_step' not in st.session_state:
            st.session_state.appt_step = 1
            st.session_state.appt_data = {}

        step = st.session_state.appt_step
        st.write(f"Step {step} of 3")

        # Step 1: Reason and Provider
        if step == 1:
            st.markdown("### Select Reason / Provider")
            reason = st.selectbox("Reason for visit", ["Annual Checkup", "Sick Visit", "Follow-up", "Prescription Refill"])            
            # providers are users with usertype 'Doctor'
            doctors = get_all_doctors()
            doc_map = {d['username']: d['id'] for d in doctors} if doctors else {}
            provider = st.selectbox("Select provider", options=["-- any --"] + list(doc_map.keys()))
            if st.button("Next"):
                st.session_state.appt_data['reason'] = reason
                st.session_state.appt_data['provider'] = doc_map.get(provider) if provider != "-- any --" else None
                st.session_state.appt_step = 2
                st.experimental_rerun()

        # Step 2: Date & Time
        elif step == 2:
            st.markdown("### Select Date & Time")
            appt_date = st.date_input("Choose a date")
            # simple demo slots
            slots = ["09:00", "10:00", "11:00", "14:00", "15:00"]
            appt_time = st.selectbox("Choose time slot", slots)
            colc, cold = st.columns(2)
            with colc:
                if st.button("Back"):
                    st.session_state.appt_step = 1
                    st.experimental_rerun()
            with cold:
                if st.button("Next"):
                    st.session_state.appt_data['date'] = str(appt_date)
                    st.session_state.appt_data['time'] = appt_time
                    st.session_state.appt_step = 3
                    st.experimental_rerun()

        # Step 3: Confirmation & Pre-Check-in
        elif step == 3:
            st.markdown("### Confirm Booking & Pre-Check-in")
            apd = st.session_state.appt_data
            st.write("**Reason:**", apd.get('reason'))
            prov_name = None
            if apd.get('provider'):
                # try to lookup provider name
                prov = get_user_by_id(apd.get('provider'))
                prov_name = prov['username'] if prov else 'Selected Provider'
            else:
                prov_name = 'Any available provider'
            st.write("**Provider:**", prov_name)
            st.write("**Date:**", apd.get('date'))
            st.write("**Time:**", apd.get('time'))

            st.markdown("#### Pre-Check-in")
            ch1 = st.checkbox("Verify insurance information is up to date", value=True)
            ch2 = st.checkbox("Confirm contact phone number", value=True)
            ch3 = st.checkbox("Complete intake form (not required in demo)")

            if st.button("Back"):
                st.session_state.appt_step = 2
                st.experimental_rerun()

            if st.button("Confirm Booking"):
                # Save appointment
                ok, msg = save_appointment(user['id'], apd.get('provider'), apd.get('reason'), apd.get('date'), apd.get('time'))
                if ok:
                    st.success(msg)
                    # reset flow
                    st.session_state.appt_step = 1
                    st.session_state.appt_data = {}
                else:
                    st.error(msg)

        # Show upcoming appointments for user
        st.markdown("---")
        st.markdown("### Your Upcoming Appointments")
        my_appts = get_user_appointments(user['id'])
        if my_appts:
            st.table(pd.DataFrame(my_appts))
        else:
            st.info("You have no upcoming appointments.")

    with tab4:
        st.subheader("💊 My Medications")
        st.markdown("Use this screen to track medications, mark doses taken, and request refills.")

        # Add medication form
        with st.expander("Add Medication"):
            with st.form("add_med_form"):
                med_name = st.text_input("Medication Name")
                med_dosage = st.text_input("Dosage (e.g., 10 mg)")
                med_schedule = st.text_input("Schedule (e.g., Twice daily - 8:00 AM & 8:00 PM)")
                med_days = st.number_input("Days supply", min_value=1, max_value=365, value=30)
                if st.form_submit_button("Add Medication"):
                    ok, msg = save_medication(user['id'], med_name, med_dosage, med_schedule, med_days)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

        # List medications
        meds = get_user_medications(user['id'])
        if meds:
            for m in meds:
                st.markdown("<div class='ch-card'>", unsafe_allow_html=True)
                cols = st.columns([3,1,1])
                with cols[0]:
                    st.markdown(f"**{m['name']}**  ")
                    st.markdown(f"{m.get('dosage','')} — {m.get('schedule','')}")
                    st.markdown(f"<div class='small-muted'>Days supply: {m.get('days_supply',0)}</div>", unsafe_allow_html=True)
                with cols[1]:
                    if st.button(f"Mark as Taken", key=f"taken_{m['id']}"):
                        if mark_medication_taken(m['id']):
                            st.success("Marked as taken")
                        else:
                            st.error("Failed to update")
                with cols[2]:
                    if m.get('refill_requested',0):
                        st.markdown("<div class='small-muted'>Refill requested</div>", unsafe_allow_html=True)
                    else:
                        if st.button(f"Request Refill", key=f"refill_{m['id']}"):
                            if request_refill(m['id']):
                                st.success("Refill requested")
                            else:
                                st.error("Failed to request refill")
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No medications yet. Add one above.")
    
    if st.button("🚪 Logout"):
        st.session_state.user = None
        st.session_state.page = 'home'
        st.rerun()

def page_doctor_dashboard():
    """Doctor dashboard."""
    if not st.session_state.user:
        st.session_state.page = 'home'
        st.rerun()
    
    user = st.session_state.user
    st.title(f"👨‍⚕️ Doctor Dashboard - {user['username']}")
    
    st.subheader("📋 Doctor Tools")

    tab_all, tab_trend, tab_stats, tab_risk, tab_access = st.tabs([
        "All Patient Data", "Trend Analysis", "Cohort Statistics", "Risk Dashboard", "Access Management"
    ])

    # All Patient Data
    with tab_all:
        st.write("All patient records (encrypted preview)")
        all_data = get_all_patient_data()
        if all_data:
            df_data = []
            for p in all_data:
                enc_parts = p['patient_data'].split(",") if p['patient_data'] else ['', '']
                df_data.append({
                    'Patient': p['username'],
                    'Date': p['predict_date'],
                    'Prediction': p['predict'],
                    'Encrypted': enc_parts[0][:50] + "..." if len(enc_parts[0]) > 50 else enc_parts[0],
                    'Symptoms': enc_parts[1] if len(enc_parts) > 1 else ''
                })
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No patient data available yet.")

    # Trend Analysis
    with tab_trend:
        st.write("View per-patient trend changes for a selected feature")
        doctors_patients = get_authorized_patients(user['id'])
        patient_options = {p['username']: p['id'] for p in doctors_patients} if doctors_patients else {}
        selected_patient = st.selectbox("Select patient", options=["-- select --"] + list(patient_options.keys()))
        feature_index = st.number_input("Feature index (0-based)", min_value=0, max_value=20, value=4)
        if st.button("Compute Trend") and selected_patient != "-- select --":
            pid = patient_options[selected_patient]
            diff = calculate_trend_difference(pid, feature_index)
            if diff is None:
                st.info("Not enough records to compute trend for this patient")
            else:
                st.metric(label="Trend Difference (current - previous)", value=diff)

    # Cohort Statistics
    with tab_stats:
        st.write("Compute cohort statistics for a symptom (simulated encrypted aggregation)")
        symptom_idx = st.number_input("Symptom index (0-based)", min_value=0, max_value=20, value=4)
        if st.button("Compute Cohort Stats"):
            stats = calculate_encrypted_statistics(symptom_idx)
            if stats.get('count', 0) == 0:
                st.info("No data to compute statistics")
            else:
                st.metric("Count", stats.get('count', 0))
                st.metric("Average", round(stats.get('average', 0), 2))
                st.metric("Min", stats.get('min', 0))
                st.metric("Max", stats.get('max', 0))

    # Risk Dashboard
    with tab_risk:
        st.write("Compute and view risk scores for a patient (simulated)")
        patients = get_authorized_patients(user['id'])
        # If the doctor has no explicitly authorized patients, fall back to all patients in DB
        if not patients:
            all_data = get_all_patient_data()
            # unique usernames
            uniq = []
            for r in all_data:
                if r['username'] not in uniq:
                    uniq.append(r['username'])
            patient_map = {}
            for uname in uniq:
                urow = get_user_by_username(uname)
                if urow:
                    patient_map[uname] = urow['id']
        else:
            patient_map = {p['username']: p['id'] for p in patients}

        sel = st.selectbox("Select patient for risk", options=["-- select --"] + list(patient_map.keys()))
        if st.button("Compute Risk") and sel != "-- select --":
            pid = patient_map.get(sel)
            # fetch last symptoms for this patient
            preds = [r for r in get_all_patient_data() if r['username'] == sel]
            if not preds:
                st.info("No records for selected patient")
            else:
                # Use the latest record's plaintext symptoms if available
                latest = preds[0]
                enc_parts = latest['patient_data'].split(",") if latest['patient_data'] else ['', '']
                symptoms_plain = []
                if len(enc_parts) > 1:
                    try:
                        symptoms_plain = [float(x) for x in enc_parts[1].split()]
                    except Exception:
                        symptoms_plain = []

                if symptoms_plain:
                    score, level = calculate_granular_risk_score(symptoms_plain)
                    save_risk_score(pid, score, level)
                    st.metric("Risk Score", f"{score} / 100")
                    st.write("Risk Level:", level)
                else:
                    st.info("Plaintext symptoms not available for risk calculation")

        # Show recent risk scores table
        st.subheader("Recent Risk Scores")
        if st.button("Refresh Risk Table"):
            rows = []
            # show latest 50 risk scores across patients
            conn_rows = get_all_patient_data()
            for r in conn_rows:
                rows.append({
                    'Patient': r['username'],
                    'Prediction': r['predict'],
                })
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True)
            else:
                st.info("No risk scores available yet.")

    # Access Management
    with tab_access:
        st.write("Grant or revoke doctor access to patient encrypted records")
        all_doctors = get_all_doctors()
        doctors_map = {d['username']: d['id'] for d in all_doctors} if all_doctors else {}
        # For patient selection, show all patients in system
        all_patients = [u for u in get_all_patient_data()]
        patient_usernames = sorted(list({p['username'] for p in all_patients}))
        sel_patient = st.selectbox("Select patient", options=["-- select --"] + patient_usernames)
        sel_doctor = st.selectbox("Select doctor to grant access", options=["-- select --"] + list(doctors_map.keys()))
        if st.button("Grant Access") and sel_patient != "-- select --" and sel_doctor != "-- select --":
            # resolve ids
            # find patient id
            pid = None
            for u in get_authorized_patients(user['id']):
                if u['username'] == sel_patient:
                    pid = u['id']
            # fallback: try to find user by name from all users
            if pid is None:
                # simple lookup via get_all_patient_data
                for r in get_all_patient_data():
                    if r['username'] == sel_patient:
                        # get user id via get_user_by_id is not available here; skip precise id
                        pass
            doctor_id = doctors_map.get(sel_doctor)
            if doctor_id:
                ok, message = grant_access(1, doctor_id)  # NOTE: granting for demo uses patient id=1 (placeholder)
                if ok:
                    st.success(message)
                else:
                    st.error(message)
        if st.button("Revoke Access") and sel_patient != "-- select --" and sel_doctor != "-- select --":
            doctor_id = doctors_map.get(sel_doctor)
            if doctor_id:
                revoked = revoke_access(1, doctor_id)  # NOTE: demo uses patient id=1
                if revoked:
                    st.success("Access revoked")
                else:
                    st.error("Failed to revoke access")
    
    if st.button("🚪 Logout"):
        st.session_state.user = None
        st.session_state.page = 'home'
        st.rerun()

# ==================== Main App Router ====================
def main():
    """Main app router."""
    if st.session_state.user:
        if st.session_state.user.get('usertype') == 'Patient':
            page_patient_dashboard()
        else:
            page_doctor_dashboard()
    else:
        page_map = {
            'home': page_home,
            'register': page_register,
            'patient_login': page_patient_login,
            'doctor_login': page_doctor_login,
            'patient_dashboard': page_patient_dashboard,
            'doctor_dashboard': page_doctor_dashboard
        }
        page_func = page_map.get(st.session_state.page, page_home)
        page_func()

if __name__ == "__main__":
    main()
