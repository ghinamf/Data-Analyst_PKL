#Connecting model to streamlit w/ app.py file

#Streamlit
import streamlit as st
import pandas as pd
import joblib

import mysql.connector
from mysql.connector import Error
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
import openpyxl
import os

#Directory file for saving th excel
# working_directory = r'C:\Users\Lenovo\analyst_pkl\code'
# os.makedirs(working_directory, exist_ok=True)
# os.chdir(working_directory)


# #Load the pkl
# scaler = joblib.load('scaler.pkl')
# le_status = joblib.load('le_status.pkl')
# #le_lokasi = joblib.load('le_lokasi.pkl')
# ohe = joblib.load('ohe.pkl')
# modela = joblib.load('final_model.pkl')
# feature_order = joblib.load('feature_order.pkl')

# Get the absolute path of the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load the pkl files using absolute paths
scaler_path = os.path.join(current_dir, 'scaler.pkl')
le_status_path = os.path.join(current_dir, 'le_status.pkl')
# le_lokasi_path = os.path.join(current_dir, 'le_lokasi.pkl')  # Assuming not used
ohe_path = os.path.join(current_dir, 'ohe.pkl')
model_path = os.path.join(current_dir, 'final_model.pkl')
feature_order_path = os.path.join(current_dir, 'feature_order.pkl')

scaler = joblib.load(scaler_path)
le_status = joblib.load(le_status_path)
# le_lokasi = joblib.load(le_lokasi_path)  # Assuming not used
ohe = joblib.load(ohe_path)
modela = joblib.load(model_path)
feature_order = joblib.load(feature_order_path)


# MySQL connection
# def create_connection():
#     connection = None
#     try:
#         connection = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             password="@Fng031216--",  # Ganti dengan password MySQL Anda
#             database="prediksi_keahlian"
#         )
#         if connection.is_connected():
#             st.write("Koneksi Berhasil")
#     except Error as e:
#         st.write(f"Error: '{e}'")
    
#     return connection
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE
        )
        if connection.is_connected():
            st.write("Koneksi Berhasil")
    except Error as e:
        st.write(f"Error: '{e}'")

    return connection


def insert_prediction(connection, data):
    cursor = connection.cursor()
    insert_query = """
    INSERT INTO prediction_history (DURATIONS_PERPROJECT, TOTAL_PROJECT, STATUS, LAMA_KERJA, DIVISI, GOL, Predicted_LEVEL_KEAHLIAN, Revisian_LEVEL_KEAHLIAN)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, data)
    connection.commit()
    

#Streamlit UI
st.title("Prediksi Keahlian")

# Input form for new data
total_project = st.number_input('Projek yang Telah Diselesaikan [Jumlah]')
durations_perproject = st.number_input('Total Waktu yang Dibutuhkan [Semua Projek (jam)]')
#total_project = st.number_input('Kemampuan Menyelesaikan Project [jumlah]')
status = st.selectbox('Status Kerja', le_status.classes_)
lama_kerja = st.number_input('Lama Kerja [Tahun]')
divisi = st.selectbox('Target Divisi', ohe.categories_[0])
gol = st.selectbox('Target Golongan', ohe.categories_[1])
revisian= st.selectbox('Level Keahlian yang Seharusnya', ['Pelaksana Madya', 'Pelaksana Pemula', 'Pelaksana Utama', 'Perekayasa Madya', 'Perekayasa Magang', 'Perekayasa Muda', 'Perekayasa Utama', 'Pimpinan Madya', 'Pimpinan Muda', 'Pimpinan Pemula', 'Pimpinan Utama' ])

#Condition for button
if st.button('Prediksi'):
    # Preprocess the new input data
    new_data = pd.DataFrame({
        'DURATIONS_PERPROJECT': [durations_perproject],
        'TOTAL_PROJECT': [total_project],
        'STATUS': [status],
        'LAMA_KERJA': [lama_kerja],
        'DIVISI': [divisi],
        #'LOKASI': [lokasi],
        'GOL': [gol]
    })
    
    data_simpan= new_data.copy()
    
    #Transforming data
    new_data['STATUSenc'] = le_status.transform(new_data['STATUS'])
    #new_data['LOKASIenc'] = le_lokasi.transform(new_data['LOKASI'])
    encoded_features_new = ohe.transform(new_data[['DIVISI', 'GOL']])
    encoded_df_new = pd.DataFrame(encoded_features_new, columns=ohe.get_feature_names_out(['DIVISI', 'GOL']))
    new_data = pd.concat([new_data, encoded_df_new], axis=1)
    new_data[['DURATIONS_PERPROJECT', 'TOTAL_PROJECT', 'LAMA_KERJA']] = scaler.transform(new_data[['DURATIONS_PERPROJECT', 'TOTAL_PROJECT', 'LAMA_KERJA']])
    
    #Unused columns
    #X_new = new_data.drop(columns=['STATUS', 'DIVISI', 'GOL'])
    #Ensure the input data follows the correct order
    X_new = new_data.reindex(columns=feature_order)

    
    #Prediction
    prediction = modela.predict(X_new)
    st.write(f'Hasil Prediksi: {prediction[0]}')
    
    #Add the revisian column
    data_simpan['Predicted_LEVEL_KEAHLIAN'] = prediction[0]
    data_simpan['Revisian_LEVEL_KEAHLIAN'] = revisian
    
    # Save input and prediction to Excel
    #history_file = os.path.join(working_directory, 'prediction_history2.xlsx')
    
    # Save input and prediction to MySQL
    connection = create_connection()
    
    if connection is not None:
        # Data to be inserted
        data_tuple = tuple(data_simpan.values.flatten())
        insert_prediction(connection, data_tuple)
        st.write("Data Berhasil Disimpan")
        
        # Close connection
        connection.close()
    else:
        st.write("Gagal Simpan")

    
    # try:
    #     # Load existing history file
    #     history_df = pd.read_excel(history_file)git
    #     hist= [history_df, data_simpan]
    #     history_df = pd.concat(hist, ignore_index=True)
    # except FileNotFoundError:
    #     # If file does not exist, create a new one
    #     history_df = data_simpan
        
    
    # history_df.to_excel(history_file, index=False)
    # st.write(f'Data has been saved and updated in {history_file}')

    
    # history_df.to_excel(history_file, index=False)
    # st.write(f'Data has been saved to {history_file}')
    
    # # Provide an option to download the Excel file
    # with open(history_file, 'rb') as file:
    #     btn = st.download_button(
    #         label="Unduh Riwayat Prediksi",
    #         data=file,
    #         file_name='prediction_history2.xlsx',
    #         mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    #     )
    


