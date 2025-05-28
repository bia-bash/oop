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

# Ensure all patients have IDs
for idx, p in enumerate(patients):
    if "id" not in p:
        p["id"] = f"P{idx + 1:03d}"
save_data(patient_file, patients)

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

    patient_id = st.text_input("Patient ID (e.g., P001)").strip()

    name = st.text_input("Patient Name").strip()
    age = st.number_input("Age", min_value=0)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    contact = st.text_input("Contact Number").strip()
    appointment_date = st.date_input("Appointment Date", min_value=datetime.date.today())
    appointment_time = st.text_input("Appointment Time (e.g., 02:30 PM)").strip()

    doctor_names = [d["name"] for d in doctors]
    assigned_doctor = st.selectbox("Select Doctor", doctor_names)

    medical_history = st.text_area("Medical History")
    vital_signs = st.text_area("Vital Signs")
    physical_examination = st.text_area("Physical Examination")
    laboratory_tests = st.text_area("Lab Results")
    doctor_advice = st.text_area("Doctor’s Notes")
    follow_up = st.text_area("Follow-Up (Leave empty if not required)")

    appointment_day = appointment_date.strftime("%A")
    name_valid = re.fullmatch(r"[A-Za-z\s\-']+", name)
    contact_valid = re.fullmatch(r"\+?\d{7,15}", contact)

    try:
        appt_24hr = datetime.datetime.strptime(appointment_time, "%I:%M %p").strftime("%H:%M")
        time_valid = True
    except ValueError:
        appt_24hr = ""
        time_valid = False

    if st.button("Add Patient"):
        if not patient_id:
            st.error("Patient ID is required.")
        elif any(p["id"] == patient_id for p in patients):
            st.error("This Patient ID is already in use.")
        elif not name_valid:
            st.error("Name must only contain letters, spaces, hyphens, or apostrophes.")
        elif not contact_valid:
            st.error("Contact number must be digits or start with +, 7 to 15 characters.")
        elif not appointment_time:
            st.error("Appointment time is required.")
        elif not time_valid:
            st.error("Time must be in 12-hour format like 02:30 PM.")
        elif any(p["appointment_date"] == str(appointment_date) and
                 p["appointment_time"] == appt_24hr and
                 p["assigned_doctor"] == assigned_doctor
                 for p in patients if p.get("is_active", True)):
            st.error(f"Doctor is already booked at that time on {appointment_date}.")
        else:
            new_patient = {
                "id": patient_id,
                "name": name,
                "age": age,
                "gender": gender,
                "contact": contact,
                "appointment_date": str(appointment_date),
                "appointment_time": appt_24hr,
                "appointment_day": appointment_day,
                "assigned_doctor": assigned_doctor,
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
            st.success(f"Patient added and assigned to {assigned_doctor} on {appointment_day}.")

# --- View Patients ---
elif menu == "View Patients":
    st.subheader("Registered Patients")
    active_patients = [p for p in patients if p.get("is_active", True)]

    if active_patients:
        for i, p in enumerate(active_patients, start=1):
            time_12hr = datetime.datetime.strptime(p['appointment_time'], "%H:%M").strftime("%I:%M %p")
            st.write(
                f"*{i}. {p['name']} (ID: {p.get('id', 'N/A')})* - Age: {p['age']}, Gender: {p['gender']}, Contact: {p['contact']}  \n"
                f"Appointment: {p['appointment_date']} at {time_12hr} ({p['appointment_day']}) with {p['assigned_doctor']}"
            )
            if st.button(f"Remove {p['name']}", key=f"remove_{i}"):
                p["is_active"] = False
                save_data(patient_file, patients)
                st.success(f"{p['name']} removed.")
                st.rerun()
    else:
        st.info("No registered patients.")

# --- View Doctors ---
elif menu == "View Doctors":
    st.subheader("Doctors")
    for d in doctors:
        st.write(f"{d['name']}")

# --- View All Patients ---
elif menu == "View All Patients":
    st.subheader("All Patients Data")
    search_name = st.text_input("Search by patient name").strip().lower()
    filtered_patients = [p for p in patients if search_name in p['name'].lower()]

    if filtered_patients:
        for i, p in enumerate(filtered_patients, start=1):
            time_12hr = datetime.datetime.strptime(p['appointment_time'], "%H:%M").strftime("%I:%M %p")
            st.markdown(f"""
*{i}. {p['name']} (ID: {p.get('id', 'N/A')})*
- Age: {p['age']}
- Gender: {p['gender']}
- Contact: {p['contact']}
- Appointment: {p['appointment_date']} at {time_12hr} ({p['appointment_day']})
- Doctor: {p['assigned_doctor']}
- Medical History: {p['medical_history']}
- Vital Signs: {p['vital_signs']}
- Physical Examination: {p['physical_examination']}
- Lab Results: {p['laboratory_tests']}
- Doctor’s Notes: {p['doctor_advice']}
- Follow-Up: {p['follow_up']}
""")
        if st.button("Print All Patients"):
            st.write("\n".join([f"{i+1}. {p['name']} ({p['appointment_date']}) - {p['assigned_doctor']}" for i, p in enumerate(filtered_patients)]))
    else:
        st.info("No matching patients found.")

# --- Follow-Up Patients ---
elif menu == "Follow-Up Patients":
    st.subheader("Patients Needing Follow-Up")
    follow_ups = [p for p in patients if p['follow_up']]
    doctor_filter = st.selectbox("Filter by Doctor", ["All"] + sorted(set(p['assigned_doctor'] for p in follow_ups)))

    if doctor_filter != "All":
        follow_ups = [p for p in follow_ups if p['assigned_doctor'] == doctor_filter]

    if follow_ups:
        for i, p in enumerate(follow_ups, start=1):
            st.write(f"*{i}. {p['name']} (ID: {p.get('id', 'N/A')})* - Follow-Up: {p['follow_up']} - Doctor: {p['assigned_doctor']}")
            if st.button(f"Remove {p['name']} from Follow-Up", key=f"remove_follow_up_{i}"):
                p['follow_up'] = ''
                save_data(patient_file, patients)
                st.success(f"{p['name']} removed from follow-up.")
                st.rerun()
    else:
        st.info("No patients marked for follow-up.")

# --- Patient Schedule ---
elif menu == "Patient Schedule":
    st.subheader("Patient Appointment Schedule")
    active_patients = [p for p in patients if p.get("is_active", True)]
    if not active_patients:
        st.info("No scheduled patients.")
    else:
        all_dates = sorted(set(p["appointment_date"] for p in active_patients))
        all_doctors = sorted(set(p["assigned_doctor"] for p in active_patients))

        selected_date = st.selectbox("Filter by Date", ["All"] + all_dates)
        selected_doctor = st.selectbox("Filter by Doctor", ["All"] + all_doctors)

        filtered = active_patients
        if selected_date != "All":
            filtered = [p for p in filtered if p["appointment_date"] == selected_date]
        if selected_doctor != "All":
            filtered = [p for p in filtered if p["assigned_doctor"] == selected_doctor]

        if filtered:
            from datetime import datetime as dt
            filtered.sort(key=lambda p: dt.strptime(p["appointment_date"] + " " + p["appointment_time"], "%Y-%m-%d %H:%M"))
            for i, p in enumerate(filtered, start=1):
                time_12hr = datetime.datetime.strptime(p['appointment_time'], "%H:%M").strftime("%I:%M %p")
                st.markdown(f"""
                **{i}. {p['name']} (ID: {p.get('id', 'N/A')})**
                - 🗓 Appointment: {p['appointment_date']} at {time_12hr} ({p['appointment_day']})
                - 👨‍⚕️ Doctor: {p['assigned_doctor']}
                """)
        else:
            st.warning("No matching scheduled patients.")
