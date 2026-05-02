# sheets.py — koneksi ke Google Sheets
import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import pytz

def get_sheet():
    """Koneksi ke Google Sheets pakai credentials dari Streamlit Secrets."""
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds  = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gcp_service_account"], scope
    )
    client = gspread.authorize(creds)
    sheet  = client.open_by_key("1fRAacHvAVmgJFgYby28HSJCic7MjlFsltzEGKF5IfUo").sheet1
    return sheet

def save_to_sheets(nama, kota, genre, mood, durasi):
    """Simpan data kuesioner ke Google Sheets."""
    try:
        sheet = get_sheet()
        wib   = pytz.timezone("Asia/Jakarta")
        now   = datetime.now(wib).strftime("%d/%m/%Y %H:%M:%S")
        sheet.append_row([now, nama, kota, genre, mood, durasi])
        return True
    except Exception as e:
        st.error(f"Gagal simpan data: {e}")
        return False