import streamlit as st
import json
import os
import datetime
import re

# File paths
patient_file = "patients.json"
doctor_file = "doctors.json"

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

# Today's date string
today_str = datetime.date.today().strftime("%Y%m%d")

# Generate next ID for today
def get_next_patient_id():
    today_patients = [p for p in patients if p.get("id", "").startswith(today_str)]
    next_number = len(today_patients) + 1
    return f"{today_str}-{next_number:03d}"

menu = st.sidebar.selectbox("Menu", [
    "Add Patient", "View Patients"
])

# --- Add Patient ---
if menu == "Add Patient":
    st.subheader("Register New Patient")

    patient_id = get_next_patient_id()
    st.text_input("Patient ID", value=patient_id, disabled=True)

    name = st.text_input("Patient Name").strip()
    age = st.number_input("Age", min_value=0)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    contact = st.text_input("Contact Number").strip()
    appointment_date = st.date_input("Appointment Date", min_value=datetime.date.today())
    appointment_time = st.text_input("Appointment Time (e.g., 02:30 PM)").strip()
    selected_doctor = st.selectbox("Select Doctor", [d["name"] for d in doctors])

    medical_history = st.text_area("Medical History")
    vital_signs = st.text_area("Vital Signs")
    physical_examination = st.text_area("Physical Examination")
    laboratory_tests = st.text_area("Lab Results")
    doctor_advice = st.text_area("Doctor’s Notes")
    follow_up = st.text_area("Follow-Up (Leave empty if not required)")

    # Validations
    name_valid = re.fullmatch(r"[A-Za-z\s\-']+", name)
    contact_valid = re.fullmatch(r"\+?\d{7,15}", contact)

    try:
        appt_24hr = datetime.datetime.strptime(appointment_time, "%I:%M %p").strftime("%H:%M")
        time_valid = True
    except ValueError:
        appt_24hr = ""
        time_valid = False

    # Double booking prevention
    double_booked = any(
        p for p in patients if p.get("appointment_date") == str(appointment_date)
        and p.get("appointment_time") == appt_24hr
        and p.get("assigned_doctor") == selected_doctor
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
            st.error("This doctor already has an appointment at the selected date and time.")
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

# --- View Patients ---
elif menu == "View Patients":
    st.subheader("Registered Patients")
    active_patients = [p for p in patients if p.get("is_active", True)]

    if active_patients:
        for i, p in enumerate(active_patients, start=1):
            try:
                time_12hr = datetime.datetime.strptime(p['appointment_time'], "%H:%M").strftime("%I:%M %p")
            except:
                time_12hr = p['appointment_time']
            st.write(
                f"*{i}. {p['name']} (ID: {p.get('id', 'N/A')})* - Age: {p['age']}, Gender: {p['gender']}, Contact: {p['contact']}  \n"
                f"Appointment: {p['appointment_date']} at {time_12hr} ({p.get('appointment_day', 'N/A')}) with {p['assigned_doctor']}"
            )
            if st.button(f"Remove {p['name']}", key=f"remove_{i}"):
                p["is_active"] = False
                save_data(patient_file, patients)
                st.success(f"{p['name']} removed.")
                st.rerun()
    else:
        st.info("No registered patients.")
