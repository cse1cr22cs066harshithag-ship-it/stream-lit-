"""
Database utilities for Streamlit CloudHealthCare app.
Supports SQLite (local dev) and PostgreSQL (production on Streamlit Cloud).
"""
import sqlite3
import os
import json
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple

DB_PATH = "cloudhealthcare.db"


def get_connection():
    """Get database connection (SQLite for local dev)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database schema if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create UserSignup table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_signup (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone_no TEXT,
            email TEXT,
            address TEXT,
            description TEXT,
            usertype TEXT
        )
    """)
    
    # Create PatientData table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patientdata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            patient_data TEXT,
            predict TEXT,
            predict_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_signup(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()


def register_user(username: str, password: str, phone_no: str, email: str, 
                  address: str, description: str, usertype: str) -> Tuple[bool, str]:
    """Register a new user. Returns (success, message)."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM user_signup WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False, f"Username '{username}' already exists"
        
        # Insert new user
        cursor.execute("""
            INSERT INTO user_signup (username, password, phone_no, email, address, description, usertype)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username, password, phone_no, email, address, description, usertype))
        
        conn.commit()
        conn.close()
        return True, "Registration successful! You can now login."
    except Exception as e:
        return False, f"Registration error: {str(e)}"


def login_user(username: str, password: str, usertype: str) -> Tuple[bool, Optional[Dict]]:
    """Login user. Returns (success, user_dict or None)."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, username, usertype FROM user_signup 
            WHERE username = ? AND password = ? AND usertype = ?
        """, (username, password, usertype))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return True, {
                'id': row['id'],
                'username': row['username'],
                'usertype': row['usertype']
            }
        else:
            return False, None
    except Exception as e:
        return False, None


def save_patient_data(user_id: int, patient_data: str, predict: str, 
                      predict_date: date) -> Tuple[bool, str]:
    """Save patient data. Returns (success, message)."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO patientdata (user_id, patient_data, predict, predict_date)
            VALUES (?, ?, ?, ?)
        """, (user_id, patient_data, predict, str(predict_date)))
        
        conn.commit()
        conn.close()
        return True, "Patient data saved successfully"
    except Exception as e:
        return False, f"Error saving patient data: {str(e)}"


def get_user_predictions(user_id: int) -> List[Dict]:
    """Get all predictions for a user."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT u.username, p.patient_data, p.predict, p.predict_date, p.created_at
            FROM patientdata p
            JOIN user_signup u ON p.user_id = u.id
            WHERE p.user_id = ?
            ORDER BY p.created_at DESC
        """, (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching predictions: {e}")
        return []


def get_all_patient_data() -> List[Dict]:
    """Get all patient data (for doctor view)."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT u.username, p.patient_data, p.predict, p.predict_date
            FROM patientdata p
            JOIN user_signup u ON p.user_id = u.id
            ORDER BY p.predict_date DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching all patient data: {e}")
        return []


def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, usertype FROM user_signup WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None


def get_user_by_username(username: str) -> Optional[Dict]:
    """Get user row by username."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, usertype FROM user_signup WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    except Exception as e:
        print(f"Error fetching user by username: {e}")
        return None


# ==================== Advanced Features ====================

def create_trend_analysis_tables():
    """Create tables for trend analysis and risk scores."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Risk scores table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS risk_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            score REAL,
            risk_level TEXT,
            calculation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_signup(id) ON DELETE CASCADE
        )
    """)
    
    # Access control table (for collaborative diagnosis)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_control (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_user_id INTEGER NOT NULL,
            authorized_doctor_id INTEGER NOT NULL,
            access_granted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_user_id) REFERENCES user_signup(id) ON DELETE CASCADE,
            FOREIGN KEY (authorized_doctor_id) REFERENCES user_signup(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()


def create_appointments_table():
    """Create appointments table for scheduling."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            provider_id INTEGER,
            reason TEXT,
            appt_date DATE,
            appt_time TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_signup(id) ON DELETE CASCADE,
            FOREIGN KEY (provider_id) REFERENCES user_signup(id) ON DELETE SET NULL
        )
    """)
    conn.commit()
    conn.close()


def save_appointment(user_id: int, provider_id: Optional[int], reason: str, appt_date: str, appt_time: str) -> Tuple[bool, str]:
    """Save an appointment booking."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO appointments (user_id, provider_id, reason, appt_date, appt_time)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, provider_id, reason, appt_date, appt_time))
        conn.commit()
        conn.close()
        return True, "Appointment booked successfully"
    except Exception as e:
        return False, f"Error saving appointment: {e}"


def get_user_appointments(user_id: int) -> List[Dict]:
    """Retrieve appointments for a user."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, a.reason, a.appt_date, a.appt_time, u.username as provider
            FROM appointments a
            LEFT JOIN user_signup u ON a.provider_id = u.id
            WHERE a.user_id = ?
            ORDER BY a.appt_date DESC, a.appt_time DESC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching appointments: {e}")
        return []


def create_medications_table():
    """Create medications table for medication manager."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            dosage TEXT,
            schedule TEXT,
            days_supply INTEGER DEFAULT 30,
            last_taken TIMESTAMP,
            refill_requested INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_signup(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()


def save_medication(user_id: int, name: str, dosage: str, schedule: str, days_supply: int) -> Tuple[bool, str]:
    """Add a medication for a user."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO medications (user_id, name, dosage, schedule, days_supply)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, name, dosage, schedule, days_supply))
        conn.commit()
        conn.close()
        return True, "Medication added"
    except Exception as e:
        return False, f"Error saving medication: {e}"


def get_user_medications(user_id: int) -> List[Dict]:
    """Get medications for a user."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, dosage, schedule, days_supply, last_taken, refill_requested
            FROM medications
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching medications: {e}")
        return []


def mark_medication_taken(med_id: int) -> bool:
    """Update last_taken timestamp for a medication."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE medications SET last_taken = CURRENT_TIMESTAMP WHERE id = ?", (med_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error marking medication taken: {e}")
        return False


def request_refill(med_id: int) -> bool:
    """Set refill_requested flag for medication."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE medications SET refill_requested = 1 WHERE id = ?", (med_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error requesting refill: {e}")
        return False


def save_risk_score(user_id: int, score: float, risk_level: str) -> bool:
    """Save calculated risk score for a patient."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO risk_scores (user_id, score, risk_level)
            VALUES (?, ?, ?)
        """, (user_id, score, risk_level))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving risk score: {e}")
        return False


def get_risk_scores(user_id: int) -> List[Dict]:
    """Get risk score history for a patient."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, score, risk_level, calculation_date FROM risk_scores
            WHERE user_id = ?
            ORDER BY calculation_date DESC
            LIMIT 30
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching risk scores: {e}")
        return []


def grant_access(patient_id: int, doctor_id: int) -> Tuple[bool, str]:
    """Grant doctor access to patient's encrypted data."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if access already exists
        cursor.execute("""
            SELECT id FROM access_control 
            WHERE patient_user_id = ? AND authorized_doctor_id = ?
        """, (patient_id, doctor_id))
        
        if cursor.fetchone():
            conn.close()
            return False, "Access already granted to this doctor"
        
        cursor.execute("""
            INSERT INTO access_control (patient_user_id, authorized_doctor_id)
            VALUES (?, ?)
        """, (patient_id, doctor_id))
        
        conn.commit()
        conn.close()
        return True, "Access granted successfully"
    except Exception as e:
        return False, f"Error granting access: {str(e)}"


def revoke_access(patient_id: int, doctor_id: int) -> bool:
    """Revoke doctor's access to patient's encrypted data."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM access_control 
            WHERE patient_user_id = ? AND authorized_doctor_id = ?
        """, (patient_id, doctor_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error revoking access: {e}")
        return False


def get_authorized_patients(doctor_id: int) -> List[Dict]:
    """Get all patients a doctor has access to."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT u.id, u.username 
            FROM access_control ac
            JOIN user_signup u ON ac.patient_user_id = u.id
            WHERE ac.authorized_doctor_id = ?
        """, (doctor_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching authorized patients: {e}")
        return []


def get_all_doctors() -> List[Dict]:
    """Get list of all doctors for access control UI."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, username FROM user_signup WHERE usertype = 'Doctor'
        """)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching doctors: {e}")
        return []


def calculate_encrypted_statistics(symptom_index: int) -> Dict:
    """
    Calculate encrypted group statistics (sum, average) for a symptom across all patients.
    This simulates Homomorphic Addition on encrypted data.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Fetch all plaintext symptoms (in real HE, these would be encrypted)
        cursor.execute("SELECT patient_data FROM patientdata")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {"count": 0, "sum": 0, "average": 0}
        
        values = []
        for row in rows:
            try:
                # Parse plaintext symptoms from comma-separated string
                parts = row['patient_data'].split(",")
                if len(parts) > 1:
                    symptoms_str = parts[-1]  # Last part is plaintext
                    symptoms = [float(x) for x in symptoms_str.split()]
                    if symptom_index < len(symptoms):
                        values.append(symptoms[symptom_index])
            except Exception:
                continue
        
        if values:
            return {
                "count": len(values),
                "sum": sum(values),
                "average": sum(values) / len(values),
                "min": min(values),
                "max": max(values)
            }
        return {"count": 0, "sum": 0, "average": 0, "min": 0, "max": 0}
    except Exception as e:
        print(f"Error calculating statistics: {e}")
        return {}


def calculate_trend_difference(user_id: int, feature_index: int) -> Optional[float]:
    """
    Calculate encrypted difference (current - previous) for trend analysis.
    Simulates Homomorphic Subtraction.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get last two records for this user
        cursor.execute("""
            SELECT patient_data FROM patientdata
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 2
        """, (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if len(rows) < 2:
            return None
        
        values = []
        for row in rows:
            try:
                parts = row['patient_data'].split(",")
                if len(parts) > 1:
                    symptoms_str = parts[-1]
                    symptoms = [float(x) for x in symptoms_str.split()]
                    if feature_index < len(symptoms):
                        values.append(symptoms[feature_index])
            except Exception:
                continue
        
        if len(values) == 2:
            return values[0] - values[1]  # Current - Previous
        return None
    except Exception as e:
        print(f"Error calculating trend: {e}")
        return None


def calculate_granular_risk_score(symptoms: list) -> Tuple[float, str]:
    """
    Calculate granular risk score (0-100) using weighted sum of symptoms.
    Simulates Homomorphic Addition and Multiplication on encrypted data.
    """
    # Weights for each symptom (adjusted based on medical importance)
    weights = [0.5, 0.3, 1.0, 1.5, 1.2, 0.8, 0.9, 0.7, 0.6, 0.4, 0.5, 0.6, 0.8]
    
    try:
        score = 0.0
        for i, symptom in enumerate(symptoms):
            if i < len(weights):
                score += float(symptom) * weights[i]
        
        # Normalize to 0-100
        normalized_score = min(100.0, (score / 50.0) * 100)
        
        # Determine risk level
        if normalized_score < 30:
            risk_level = "Low Risk"
        elif normalized_score < 60:
            risk_level = "Moderate Risk"
        elif normalized_score < 80:
            risk_level = "High Risk"
        else:
            risk_level = "Critical Risk"
        
        return round(normalized_score, 2), risk_level
    except Exception as e:
        print(f"Error calculating risk score: {e}")
        return 0.0, "Unknown"


# Initialize advanced tables on import
create_trend_analysis_tables()
create_appointments_table()
create_medications_table()
