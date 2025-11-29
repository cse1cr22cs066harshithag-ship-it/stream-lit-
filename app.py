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
from streamlit_db import init_db, register_user, login_user, save_patient_data, get_user_predictions, get_all_patient_data, get_user_by_id

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
    st.title(f"👤 Patient Dashboard - {user['username']}")
    
    tab1, tab2 = st.tabs(["Upload Symptoms", "View Predictions"])
    
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
                
                # Encrypt symptoms
                encrypted = encrypt_symptoms(symptoms)
                plaintext = " ".join(str(s) for s in symptoms)
                
                # Make prediction
                prediction = make_prediction(symptoms)
                
                # Save to DB
                patient_data = encrypted + "," + plaintext
                success, msg = save_patient_data(user['id'], patient_data, prediction, date.today())
                
                if success:
                    st.success(msg)
                    st.info(f"**Prediction: {prediction}**")
                    st.text(f"Encrypted Data: {encrypted}")
                else:
                    st.error(msg)
    
    with tab2:
        st.subheader("📊 Your Predictions")
        predictions = get_user_predictions(user['id'])
        
        if predictions:
            # Convert to DataFrame for nice display
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
        else:
            st.info("No predictions yet. Upload some symptoms to get started!")
    
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
    
    st.subheader("📋 All Patient Data")
    
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
