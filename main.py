import streamlit as st
import json
import os
import datetime
import re

# File paths
patient_file = "patients.json"
doctor_file = "doctors.json"
id_tracker_file = "id_tracker.json"

st.title("SmartCare: Efficient Healthcare Management System")

# Load & Save

def load_data(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return []

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def load_id_tracker():
    if os.path.exists(id_tracker_file):
        with open(id_tracker_file, "r") as f:
            return json.load(f)
    return {"date": str(datetime.date.today()), "last_id": 0}

def save_id_tracker(data):
    with open(id_tracker_file, "w") as f:
        json.dump(data, f)

# Load data
patients = load_data(patient_file)
doctors = load_data(doctor_file)

# Default doctors
if not doctors:
    doctors = [
        {"name": "Dr. Kia Bannca P. Marabe, General Physician"},
        {"name": "Dr. JR M., Pediatrician"}
    ]
    save_data(doctor_file, doctors)

menu = st.sidebar.selectbox("Menu", [
    "Add Patient", "View Patients", "View Doctors", "View All Patients",
    "Follow-Up Patients", "Patient Schedule"
])

# --- Add Patient ---
if menu == "Add Patient":
    st.subheader("Register New Patient")

    # Generate daily ID
    id_data = load_id_tracker()
    today = str(datetime.date.today())
    if id_data["date"] != today:
        id_data = {"date": today, "last_id": 1}
    else:
        id_data["last_id"] += 1
    patient_id = f"{today}-{id_data['last_id']}"
    save_id_tracker(id_data)

    st.text_input("Generated Patient ID", value=patient_id, disabled=True)

    name = st.text_input("Patient Name").strip()
    age = st.number_input("Age", min_value=0)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    contact = st.text_input("Contact Number").strip()
    appointment_date = st.date_input("Appointment Date", min_value=datetime.date.today())
    appointment_time = st.text_input("Appointment Time (e.g., 02:30 PM)").strip()
    selected_doctor = st.selectbox("Select Doctor", [doc["name"] for doc in doctors])

    medical_history = st.text_area("Medical History")
    vital_signs = st.text_area("Vital Signs")
    physical_examination = st.text_area("Physical Examination")
    laboratory_tests = st.text_area("Lab Results")
    doctor_advice = st.text_area("Doctor’s Notes")
    follow_up = st.text_area("Follow-Up (Leave empty if not required)")

    name_valid = re.fullmatch(r"[A-Za-z\s\-']+", name)
    contact_valid = re.fullmatch(r"\+?\d{7,15}", contact)

    try:
        appt_24hr = datetime.datetime.strptime(appointment_time, "%I:%M %p").strftime("%H:%M")
        time_valid = True
    except ValueError:
        appt_24hr = ""
        time_valid = False

    # Check for double booking
    double_booked = any(
        p for p in patients if p["appointment_date"] == str(appointment_date)
        and p["appointment_time"] == appt_24hr and p["assigned_doctor"] == selected_doctor
    )

    if st.button("Add Patient"):
        if not name_valid:
            st.error("Name must only contain letters, spaces, hyphens, or apostrophes.")
        elif not contact_valid:
            st.error("Contact number must be digits or start with +, 7 to 15 characters.")
        elif not appointment_time:
            st.error("Appointment time is required.")
        elif not time_valid:
            st.error("Time must be in 12-hour format like 02:30 PM.")
        elif double_booked:
            st.error("This time slot is already booked for the selected doctor.")
        else:
            new_patient = {
                "id": patient_id,
                "name": name,
                "age": age,
                "gender": gender,
                "contact": contact,
                "appointment_date": str(appointment_date),
                "appointment_time": appt_24hr,
                "appointment_day": appointment_date.strftime("%A"),
                "assigned_doctor": selected_doctor,
                "medical_history": medical_history,
                "vital_signs": vital_signs,
                "physical_examination": physical_examination,
                "laboratory_tests": laboratory_tests,
                "doctor_advice": doctor_advice,
                "follow_up": follow_up,
                "is_active": True
            }
            patients.append(new_patient)
            save_data(patient_file, patients)
            st.success(f"Patient added and assigned to {selected_doctor} on {appointment_date.strftime('%A')}.")

# The rest of the app (View Patients, View Doctors, etc.) would remain mostly the same.
# Let me know if you'd like the full app reprinted with these changes included end-to-end.
