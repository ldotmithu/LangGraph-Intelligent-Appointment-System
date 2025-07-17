
from datetime import datetime,date
import pandas as pd 
from langchain_core.tools import tool
from typing_extensions import Literal,List
from pydantic import Field
from tools.base_models import DateTimeModel,DateModel,IdentificationNumberModel

@tool
def convert_to_am_pm(time_str):
    """ convert_to_am_pm"""
    hours, minutes = map(int, time_str.split(":"))
    period = "AM" if hours < 12 else "PM"
    hours = hours % 12 or 12
    return f"{hours}:{minutes:02d} {period}"


def load_availability():
    df = pd.read_csv("Data/availability.csv")
    df['date_slot_dt'] = pd.to_datetime(df['date_slot'], format="%d-%m-%Y %H:%M")
    df['date_only'] = df['date_slot_dt'].dt.strftime('%d-%m-%Y')
    df['time_only'] = df['date_slot_dt'].dt.strftime('%H:%M')
    return df


@tool
def check_availability_by_doctor(desired_date: DateModel, doctor_name: Literal[
    'kevin anderson', 'robert martinez', 'susan davis', 'daniel miller', 'sarah wilson',
    'michael green', 'lisa brown', 'jane smith', 'emily johnson', 'john doe']) -> str:
    """ check_availability_by_doctor"""
    df = load_availability()
    rows = df[(df['date_only'] == desired_date.date) & (df['doctor_name'] == doctor_name) & (df['is_available']==True)]['time_only'].tolist()
    if not rows:
        return f"No availability for {doctor_name} on {desired_date.date}."
    slots = ", ".join(convert_to_am_pm.invoke(t) for t in rows)
    return f"Availability for {doctor_name} on {desired_date.date}: {slots}"

@tool
def check_availability_by_specialization(desired_date: DateModel, specialization: Literal[
    "general_dentist", "cosmetic_dentist", "prosthodontist", "pediatric_dentist", "emergency_dentist", "oral_surgeon", "orthodontist"]) -> str:
    """ check_availability_by_specialization"""
    df = load_availability()
    rows = df[(df['date_only'] == desired_date.date) & (df['specialization'] == specialization) & (df['is_available']==True)] \
        .groupby(['specialization', 'doctor_name'])['time_only'].apply(list).reset_index()
    if rows.empty:
        return f"No availability for {specialization} on {desired_date.date}."
    return "\n".join([f"- {row['doctor_name']}: {', '.join(convert_to_am_pm.invoke(t) for t in row['time_only'])}" for _, row in rows.iterrows()])

@tool
def set_appointment(desired_date: DateTimeModel, id_number: IdentificationNumberModel, doctor_name: Literal[
    'kevin anderson', 'robert martinez', 'susan davis', 'daniel miller', 'sarah wilson',
    'michael green', 'lisa brown', 'jane smith', 'emily johnson', 'john doe']) -> str:
    """ set_appointment"""
    df = load_availability()
    dt = datetime.strptime(desired_date.date, "%d-%m-%Y %H:%M")
    match = df[(df['doctor_name'] == doctor_name) & (df['is_available']==True) & (df['date_slot_dt'] == dt)]
    if match.empty:
        return "No available appointments for that case."
    df.loc[match.index[0], ['is_available', 'patient_to_attend']] = [False, id_number.id]
    df.to_csv("Data/availability.csv", index=False)
    return "Successfully booked the appointment."

@tool
def cancel_appointment(date: DateTimeModel, id_number: IdentificationNumberModel, doctor_name: Literal[
    'kevin anderson', 'robert martinez', 'susan davis', 'daniel miller', 'sarah wilson',
    'michael green', 'lisa brown', 'jane smith', 'emily johnson', 'john doe']) -> str:
    """cancel_appointment """
    df = load_availability()
    dt = datetime.strptime(date.date, "%d-%m-%Y %H:%M")
    idx = df[(df['date_slot_dt'] == dt) & (df['patient_to_attend'] == id_number.id) & (df['doctor_name'] == doctor_name)].index
    if idx.empty:
        return "No matching appointment found."
    df.loc[idx, ['is_available', 'patient_to_attend']] = [True, None]
    df.to_csv("Data/availability.csv", index=False)
    return "Successfully cancelled."

@tool
def reschedule_appointment(old_date: DateTimeModel, new_date: DateTimeModel, id_number: IdentificationNumberModel, doctor_name: Literal[
    'kevin anderson', 'robert martinez', 'susan davis', 'daniel miller', 'sarah wilson',
    'michael green', 'lisa brown', 'jane smith', 'emily johnson', 'john doe']) -> str:
    """ reschedule_appointment"""
    df = load_availability()
    old_dt = datetime.strptime(old_date.date, "%d-%m-%Y %H:%M")
    new_dt = datetime.strptime(new_date.date, "%d-%m-%Y %H:%M")
    new_slot = df[(df['date_slot_dt'] == new_dt) & (df['is_available']==True) & (df['doctor_name'] == doctor_name)]
    if new_slot.empty:
        return "New time not available."
    old_idx = df[(df['date_slot_dt'] == old_dt) & (df['patient_to_attend'] == id_number.id) & (df['doctor_name'] == doctor_name)].index
    if old_idx.empty:
        return "Old appointment not found."
    df.loc[old_idx, ['is_available', 'patient_to_attend']] = [True, None]
    df.loc[new_slot.index[0], ['is_available', 'patient_to_attend']] = [False, id_number.id]
    df.to_csv("Data/availability.csv", index=False)
    return "Rescheduled successfully."