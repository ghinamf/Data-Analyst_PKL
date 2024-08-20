# import os
# from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

# MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
# MYSQL_USER = os.getenv('MYSQL_USER', 'root')
# MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '@Fng031216--')  # Ganti dengan placeholder atau nilai default
# MYSQL_DATABASE = 'prediksi_keahlian'

import streamlit as st

MYSQL_HOST = st.secrets["MYSQL_HOST"]
MYSQL_USER = st.secrets["MYSQL_USER"]
MYSQL_PASSWORD = st.secrets["MYSQL_PASSWORD"]
MYSQL_DATABASE = st.secrets["MYSQL_DATABASE"]
