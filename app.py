import streamlit as st
import sqlite3
import pandas as pd
import google.generativeai as genai
from datetime import date

# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(
    page_title="Health Prediction Application",
    layout="wide"
)

# ==========================
# GEMINI CONFIG
# ==========================

genai.configure(
    api_key="YOUR_GEMINI_API_KEY"
)

model = genai.GenerativeModel("gemini-2.5-flash")

# ==========================
# DATABASE
# ==========================

conn = sqlite3.connect(
    "database.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS patients(
    id INTEGER PRIMARY KEY,
    name TEXT,
    dob TEXT,
    email TEXT,
    glucose REAL,
    haemoglobin REAL,
    cholesterol REAL,
    remarks TEXT
)
""")

conn.commit()

# ==========================
# SIDEBAR
# ==========================

menu = st.sidebar.selectbox(
    "Choose an option",
    ["Create", "Read", "Update", "Delete"]
)

st.title("🏥 Health Prediction Application")

# ==========================
# CREATE
# ==========================

if menu == "Create":

    st.header("Add Patient")

    patient_id = st.number_input(
        "Patient ID",
        min_value=1,
        step=1
    )

    name = st.text_input("Full Name")

    dob = st.date_input(
        "Date of Birth",
        value=date.today(),
        min_value=date(1950, 1, 1),
        max_value=date.today()
    )

    email = st.text_input("Email Address")

    glucose = st.number_input(
        "Glucose",
        min_value=0.0,
        max_value=500.0,
        value=100.0
    )

    haemoglobin = st.number_input(
        "Haemoglobin",
        min_value=0.0,
        max_value=30.0,
        value=13.0
    )

    cholesterol = st.number_input(
        "Cholesterol",
        min_value=0.0,
        max_value=500.0,
        value=180.0
    )

    if st.button("Save Patient"):

        cursor.execute(
            "SELECT * FROM patients WHERE id=?",
            (patient_id,)
        )

        if cursor.fetchone():
            st.error("Patient ID already exists")
            st.stop()

        if not name.strip():
            st.error("Please enter patient name")
            st.stop()

        if "@" not in email:
            st.error("Please enter valid email")
            st.stop()

        prompt = f"""
        You are a healthcare assistant.

        Glucose: {glucose}
        Haemoglobin: {haemoglobin}
        Cholesterol: {cholesterol}

        Provide:
        1. Possible health condition
        2. Risk level
        3. Recommendation

        Keep answer under 50 words.
        """

        try:
            response = model.generate_content(prompt)
            remarks = response.text

        except Exception as e:
            remarks = f"AI Prediction Error: {e}"

        cursor.execute(
            """
            INSERT INTO patients
            (
            id,
            name,
            dob,
            email,
            glucose,
            haemoglobin,
            cholesterol,
            remarks
            )
            VALUES(?,?,?,?,?,?,?,?)
            """,
            (
                patient_id,
                name,
                str(dob),
                email,
                glucose,
                haemoglobin,
                cholesterol,
                remarks
            )
        )

        conn.commit()

        st.success("Patient Saved Successfully")

# ==========================
# READ
# ==========================

elif menu == "Read":

    st.header("📋 Patient Records")

    df = pd.read_sql_query(
        "SELECT * FROM patients",
        conn
    )

    st.dataframe(
        df,
        use_container_width=True
    )

# ==========================
# UPDATE
# ==========================

elif menu == "Update":

    st.header("✏️ Update Patient")

    patient_ids = pd.read_sql_query(
        "SELECT id FROM patients",
        conn
    )["id"].tolist()

    if len(patient_ids) == 0:
        st.warning("No patients available.")
    else:

        update_id = st.selectbox(
            "Select Patient ID",
            patient_ids
        )

        new_email = st.text_input(
            "New Email"
        )

        new_glucose = st.number_input(
            "New Glucose",
            min_value=0.0,
            max_value=500.0,
            value=100.0
        )

        new_haemoglobin = st.number_input(
            "New Haemoglobin",
            min_value=0.0,
            max_value=30.0,
            value=13.0
        )

        new_cholesterol = st.number_input(
            "New Cholesterol",
            min_value=0.0,
            max_value=500.0,
            value=180.0
        )

        if st.button("Update Patient"):

            cursor.execute(
                """
                UPDATE patients
                SET
                email=?,
                glucose=?,
                haemoglobin=?,
                cholesterol=?
                WHERE id=?
                """,
                (
                    new_email,
                    new_glucose,
                    new_haemoglobin,
                    new_cholesterol,
                    update_id
                )
            )

            conn.commit()

            st.success(
                "Patient Updated Successfully"
            )

# ==========================
# DELETE
# ==========================

elif menu == "Delete":

    st.header("🗑️ Delete Patient")

    patient_ids = pd.read_sql_query(
        "SELECT id FROM patients",
        conn
    )["id"].tolist()

    if len(patient_ids) == 0:
        st.warning("No patients available.")
    else:

        delete_id = st.selectbox(
            "Select Patient ID To Delete",
            patient_ids
        )

        if st.button("Delete Patient"):

            cursor.execute(
                """
                DELETE FROM patients
                WHERE id=?
                """,
                (delete_id,)
            )

            conn.commit()

            st.success(
                "Patient Deleted Successfully"
            )

conn.close()