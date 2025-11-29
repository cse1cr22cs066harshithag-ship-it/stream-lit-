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
